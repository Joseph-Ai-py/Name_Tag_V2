from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.context_manager import build_context
from app.agent.evaluator import AgentEvaluator
from app.agent.planner import AgentPlanner
from app.agent.router import classify_message
from app.agent.state import AgentBudget, AgentExecutionState
from app.agent.validation import AgentToolValidator
from app.llm.schemas import LLMResponse
from app.models.agent_run import AgentRun
from app.models.research_job import ResearchJob
from app.models.research_report import ResearchReport
from app.models.tool_call import ToolCall
from app.models.user import User
from app.services.artifact_service import create_artifact, get_brand_artifacts
from app.services.brand_state_service import get_brand_state
from app.services.conversation_service import (
    create_conversation,
    create_message,
    get_conversation,
    get_messages,
)
from app.services.proposal_service import create_proposal, get_brand_proposals
from app.services.research_service import get_report_sources
from app.services.usage_service import record_usage, start_usage
from app.skills.executor import SkillExecutor
from app.skills.registry import skill_registry
from app.tools.base import ToolContext
from app.tools.executor import ToolExecutor
from app.tools.registry import tool_registry


DEFAULT_BUDGET = AgentBudget(max_iterations=8, max_tool_calls=8, max_llm_calls=8)


class AgentCore:
    def __init__(
        self,
        db: Session,
        user: User,
        brand_id: str,
        role: str,
        *,
        planner: AgentPlanner | None = None,
        evaluator: AgentEvaluator | None = None,
        validator: AgentToolValidator | None = None,
        tool_executor: ToolExecutor | None = None,
        skill_executor: SkillExecutor | None = None,
        budget: AgentBudget = DEFAULT_BUDGET,
    ) -> None:
        self.db = db
        self.user = user
        self.brand_id = brand_id
        self.role = role
        self.planner = planner or AgentPlanner()
        self.evaluator = evaluator or AgentEvaluator()
        self.validator = validator or AgentToolValidator()
        self.tool_executor = tool_executor or ToolExecutor()
        self.skill_executor = skill_executor or SkillExecutor()
        self.budget = budget.model_copy(deep=True)

    def run(self, conversation_id: str | None, message: str) -> dict[str, Any]:
        started_at = start_usage()
        brand_state = get_brand_state(self.db, self.brand_id)
        route = self._resolve_route(message)
        conversation = self._get_or_create_conversation(conversation_id, message)
        history = [
            {"role": item.role, "content": item.content}
            for item in get_messages(self.db, conversation.id)
        ]
        create_message(self.db, conversation, "user", message, None)

        pending_proposals = [
            {"id": item.id, "title": item.title, "summary": item.summary, "status": item.status}
            for item in get_brand_proposals(self.db, self.brand_id)
            if item.status == "pending"
        ]
        active_research = [
            {
                "id": item.id,
                "status": item.status,
                "query": item.query,
                "progress": item.progress,
            }
            for item in self.db.scalars(
                select(ResearchJob)
                .where(ResearchJob.brand_id == self.brand_id)
                .where(ResearchJob.status.not_in(("completed", "cancelled")))
                .order_by(ResearchJob.created_at.desc())
            ).all()
        ]
        recent_artifacts = [
            {"id": item.id, "type": item.type, "title": item.title, "status": item.status}
            for item in get_brand_artifacts(self.db, self.brand_id)[:10]
        ]
        recent_research_sources = []
        recent_reports = self.db.scalars(
            select(ResearchReport)
            .where(ResearchReport.brand_id == self.brand_id)
            .where(ResearchReport.status == "completed")
            .order_by(ResearchReport.created_at.desc())
            .limit(3)
        ).all()
        for report in recent_reports:
            for source in get_report_sources(self.db, report.id):
                recent_research_sources.append({
                    "report_id": report.id,
                    "report_title": report.title,
                    "title": source.title,
                    "url": source.url,
                    "publisher": source.publisher,
                })
        context = build_context(
            brand_state.state if brand_state else None,
            version=brand_state.version if brand_state else None,
            conversation_history=history,
            user_role=self.role,
            goal=message,
            initial_route=route,
            pending_proposals=pending_proposals,
            active_research=active_research,
            recent_artifacts=recent_artifacts,
        )
        context["research"]["recent_sources"] = recent_research_sources
        skill_name = self._select_skill(route, message)
        context["selected_skill"] = skill_name
        context["available_tools"] = self._available_tools()
        context["available_skills"] = self._available_skills()

        agent_run = AgentRun(
            user_id=self.user.id,
            brand_id=self.brand_id,
            conversation_id=conversation.id,
            route=route,
            message=message,
            status="running",
            context=context,
            result={},
        )
        self.db.add(agent_run)
        self.db.flush()
        execution = AgentExecutionState(
            goal=message,
            mode=self._classify_mode(route, message),
            route=route,
            budget=self.budget.model_copy(deep=True),
            base_state_version=brand_state.version if brand_state else None,
        )
        tool_context = ToolContext(
            db=self.db,
            user_id=self.user.id,
            brand_id=self.brand_id,
            role=self.role,
        )
        final_response: LLMResponse | None = None
        proposal_id: str | None = None
        artifact = None

        for _ in range(execution.budget.max_iterations):
            execution.iteration += 1
            self._sync_context(context, execution)
            evaluation = self.evaluator.evaluate(
                message,
                context,
                skill_name=skill_name,
                tool_results=execution.tool_results,
            )
            evaluation_dict = evaluation.as_dict()
            execution.evaluations.append(evaluation_dict)
            context["evaluation"] = evaluation_dict

            if execution.llm_calls >= execution.budget.max_llm_calls:
                execution.status = "budget_exceeded"
                break
            execution.llm_calls += 1
            decision = self.planner.decide(
                goal=message,
                context=context,
                state=execution,
                tools=context["available_tools"],
                skills=context["available_skills"],
                evaluation=evaluation_dict,
            )
            execution.evaluations.append({"decision": decision.model_dump()})

            if decision.action == "final":
                if decision.message:
                    final_response = LLMResponse(text=decision.message)
                    break
                if execution.llm_calls >= execution.budget.max_llm_calls:
                    execution.status = "budget_exceeded"
                    break
                execution.llm_calls += 1
                final_response = self._generate_response(skill_name, message, context, execution)
                break
            if decision.action == "ask_user":
                execution.status = "waiting_for_user"
                execution.waiting_for = "user_input"
                final_response = LLMResponse(text=decision.message or "추가 정보가 필요합니다.")
                break
            if decision.action == "wait_for_approval":
                execution.status = "waiting_for_approval"
                execution.waiting_for = "approval"
                execution.pending_resource_id = decision.pending_resource_id or decision.proposal_id
                proposal_id = decision.proposal_id
                final_response = LLMResponse(text=decision.message or "승인을 기다리고 있습니다.")
                break
            if decision.action == "replan":
                execution.evaluations.append({"replan": decision.reason})
                continue
            if decision.action == "propose":
                if execution.llm_calls >= execution.budget.max_llm_calls:
                    execution.status = "budget_exceeded"
                    break
                if decision.proposed_changes:
                    final_response = LLMResponse(
                        text=decision.proposal_summary or decision.message or "제안이 준비되었습니다.",
                        proposed_changes=decision.proposed_changes,
                    )
                    proposal_id = self._create_response_proposal(
                        final_response,
                        route,
                        execution.base_state_version,
                        title=decision.proposal_title,
                    )
                else:
                    execution.llm_calls += 1
                    final_response = self._generate_response(decision.skill_name or skill_name, message, context, execution)
                    proposal_id = self._create_response_proposal(final_response, route, execution.base_state_version)
                break
            if decision.action != "tool_call" or decision.tool_name is None:
                execution.status = "degraded"
                final_response = LLMResponse(text="요청을 안전하게 판단하지 못했습니다.")
                break

            if execution.tool_calls >= execution.budget.max_tool_calls:
                execution.status = "budget_exceeded"
                break
            tool_name = decision.tool_name
            execution.tool_calls += 1
            try:
                self.validator.validate(tool_name, decision.arguments, self.role)
            except (ValueError, PermissionError) as exc:
                execution.failed_tools.append(tool_name)
                execution.failure_code = "tool_validation_error"
                execution.failure_stage = "tool_validation"
                execution.failure_type = type(exc).__name__
                execution.evaluations.append({"tool": tool_name, "status": "validation_failed", "error": str(exc)})
                self.db.add(ToolCall(
                    agent_run_id=agent_run.id,
                    tool_name=tool_name,
                    status="failed",
                    arguments=decision.arguments,
                    result={"error": "Tool validation failed", "type": type(exc).__name__},
                ))
                continue
            try:
                result = self.tool_executor.execute(tool_name, tool_context, **decision.arguments)
                result = self._json_value(result)
                execution.tool_results[tool_name] = result
                execution.completed_steps.append(tool_name)
                execution.observations.append({"tool": tool_name, "result": result})
                self.db.add(ToolCall(
                    agent_run_id=agent_run.id,
                    tool_name=tool_name,
                    status="completed",
                    arguments=decision.arguments,
                    result=result,
                ))
                self._apply_observation(context, tool_name, result)
                if tool_name == "create_research_job" and isinstance(result, dict):
                    execution.status = "waiting_for_approval"
                    execution.waiting_for = "approval"
                    execution.pending_resource_id = result.get("job_id")
                    final_response = LLMResponse(
                        text="Research Job이 생성되었습니다. 승인 후 리서치를 시작할 수 있습니다."
                    )
                    break
                if tool_name == "get_research_job" and isinstance(result, dict):
                    job_status = result.get("status")
                    execution.pending_resource_id = result.get("job_id")
                    if job_status == "completed":
                        execution.status = "completed"
                        final_response = LLMResponse(
                            text="Research가 완료되었습니다. Research 화면에서 보고서와 근거 자료를 확인할 수 있습니다."
                        )
                    elif job_status == "failed":
                        execution.status = "degraded"
                        final_response = LLMResponse(
                            text="Research 실행이 실패했습니다. Research 화면에서 재시도할 수 있습니다."
                        )
                    else:
                        execution.status = "waiting_for_approval" if job_status in {"planning", "approved"} else "waiting_for_user"
                        execution.waiting_for = "approval" if job_status in {"planning", "approved"} else "research"
                        final_response = LLMResponse(
                            text=f"Research가 현재 '{job_status}' 상태입니다. 완료 후 Research 화면에서 결과를 확인할 수 있습니다."
                        )
                    break
            except Exception as exc:
                execution.failed_tools.append(tool_name)
                execution.failure_code = "tool_execution_error"
                execution.failure_stage = "tool_execution"
                execution.failure_type = type(exc).__name__
                execution.observations.append({"tool": tool_name, "error": str(exc)})
                execution.evaluations.append({"tool": tool_name, "status": "failed", "error": str(exc)})
                self.db.add(ToolCall(
                    agent_run_id=agent_run.id,
                    tool_name=tool_name,
                    status="failed",
                    arguments=decision.arguments,
                    result={"error": str(exc)},
                ))
                context.setdefault("agent", {}).setdefault("failed_tools", []).append(tool_name)
                context.setdefault("agent", {}).setdefault("tool_errors", {})[tool_name] = {
                    "error": str(exc),
                    "type": type(exc).__name__,
                }
                continue

        if final_response is None:
            final_response = LLMResponse(text="작업을 완료하지 못했습니다. 실행 기록을 확인해 주세요.")
        if execution.status == "running":
            if execution.failed_tools:
                execution.status = "degraded"
            else:
                execution.status = "budget_exceeded" if execution.iteration >= execution.budget.max_iterations else "completed"
        if final_response.proposed_changes and proposal_id is None:
            try:
                proposal_id = self._create_response_proposal(final_response, route, execution.base_state_version)
            except ValueError as exc:
                context["proposal_error"] = str(exc)
                execution.status = "degraded"
        if final_response.artifact_type is not None:
            artifact = create_artifact(
                db=self.db,
                brand_id=self.brand_id,
                user_id=self.user.id,
                artifact_type=final_response.artifact_type,
                title=final_response.artifact_type.replace("_", " ").title(),
                content=final_response.artifact_content,
            )
        create_message(
            db=self.db,
            conversation=conversation,
            role="assistant",
            content=final_response.text,
            artifact={"artifact_id": artifact.id} if artifact else None,
        )
        self._sync_context(context, execution)
        context["final_evaluation"] = execution.evaluations[-1] if execution.evaluations else {}
        record_usage(self.db, self.user.id, self.brand_id, "chat", started_at)
        agent_run.status = execution.status
        agent_run.context = context
        agent_run.result = {
            "route": route,
            "mode": execution.mode,
            "status": execution.status,
            "iterations": execution.iteration,
            "tools_used": execution.completed_steps,
            "tool_calls": execution.tool_calls,
            "llm_calls": execution.llm_calls,
            "failure_code": execution.failure_code,
            "failure_stage": execution.failure_stage,
            "failure_type": execution.failure_type,
            "proposal_id": proposal_id,
            "artifact_id": artifact.id if artifact else None,
        }
        agent_run.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        return {
            "conversation_id": conversation.id,
            "run_id": agent_run.id,
            "route": route,
            "message": final_response.text,
            "artifact": artifact,
            "proposal_id": proposal_id,
            "context": context,
            "execution": {
                "mode": execution.mode,
                "status": execution.status,
                "iterations": execution.iteration,
                "tools_used": execution.completed_steps,
                "tool_calls": execution.tool_calls,
                "llm_calls": execution.llm_calls,
                "failure_code": execution.failure_code,
                "failure_stage": execution.failure_stage,
                "failure_type": execution.failure_type,
                "waiting_for": execution.waiting_for,
                "pending_resource_id": execution.pending_resource_id,
            },
        }

    def _get_or_create_conversation(self, conversation_id: str | None, message: str):
        if conversation_id:
            conversation = get_conversation(self.db, conversation_id, self.brand_id)
            if conversation is None:
                raise ValueError("Conversation not found")
            return conversation
        return create_conversation(
            db=self.db,
            brand_id=self.brand_id,
            user_id=self.user.id,
            title=message[:100],
        )

    def _create_response_proposal(
        self,
        response: LLMResponse,
        route: str,
        base_state_version: int | None,
        title: str | None = None,
    ) -> str | None:
        if not response.proposed_changes:
            return None
        proposal = create_proposal(
            db=self.db,
            brand_id=self.brand_id,
            user_id=self.user.id,
            title=title or f"{route.title()} 제안",
            summary=response.text,
            changes=response.proposed_changes,
            base_state_version=base_state_version,
        )
        return proposal.id

    def _generate_response(
        self,
        skill_name: str,
        message: str,
        context: dict[str, Any],
        execution: AgentExecutionState,
    ) -> LLMResponse:
        try:
            return self.skill_executor.execute(skill_name=skill_name, message=message, context=context)
        except Exception as exc:
            execution.status = "degraded"
            execution.failure_code = "response_generation_error"
            execution.failure_stage = "response_generation"
            execution.failure_type = type(exc).__name__
            context["llm_error"] = str(exc)
            return LLMResponse(text="요청을 처리하는 동안 일부 단계가 실패했습니다.")

    @staticmethod
    def _json_value(value: Any) -> Any:
        if isinstance(value, dict):
            return {str(key): AgentCore._json_value(item) for key, item in value.items()}
        if isinstance(value, list):
            return [AgentCore._json_value(item) for item in value]
        if hasattr(value, "id") and hasattr(value, "status"):
            return {"id": value.id, "status": value.status}
        return value

    @staticmethod
    def _apply_observation(context: dict[str, Any], tool_name: str, result: Any) -> None:
        agent = context.setdefault("agent", {})
        agent.setdefault("tool_results", {})[tool_name] = result
        agent.setdefault("completed_steps", []).append(tool_name)
        if tool_name == "get_brand_state" and isinstance(result, dict):
            state = result.get("state", {})
            context["brand_state"] = {
                "version": result.get("version"),
                **state,
            }
            agent.setdefault("observed", {})["brand_state"] = True

    @staticmethod
    def _sync_context(context: dict[str, Any], execution: AgentExecutionState) -> None:
        context["agent_state"] = execution.as_dict()
        context.setdefault("agent", {})["tool_results"] = execution.tool_results
        context.setdefault("agent", {})["failed_tools"] = execution.failed_tools
        context["tool_results"] = execution.tool_results
        context["evaluations"] = execution.evaluations

    def _available_tools(self) -> list[dict[str, Any]]:
        definitions = []
        for name in tool_registry.names():
            definition = tool_registry.get(name)
            from app.agent.permissions import can_use_tool

            if can_use_tool(self.role, definition.permission) and name != "apply_brand_change":
                definitions.append({
                    "name": definition.name,
                    "description": definition.description,
                    "category": definition.category,
                    "permission": definition.permission,
                    "risk_level": definition.risk_level,
                    "input_schema": definition.input_schema,
                })
        return definitions

    @staticmethod
    def _available_skills() -> list[dict[str, Any]]:
        return [
            {
                "name": name,
                "description": skill_registry.get(name).description,
                "required_context": skill_registry.get(name).required_context,
                "dependencies": skill_registry.get(name).dependencies,
                "output_paths": skill_registry.get(name).output_paths,
                "proposal_required": skill_registry.get(name).proposal_required,
            }
            for name in skill_registry.names()
        ]

    @staticmethod
    def _resolve_route(message: str) -> str:
        route = classify_message(message)
        if any(keyword in message.casefold() for keyword in ("포지셔닝", "positioning")):
            return "brand"
        return route

    @staticmethod
    def _classify_mode(route: str, message: str) -> str:
        normalized = message.casefold()
        if route in {"research", "brand"} and any(
            keyword in normalized for keyword in ("전면", "시장", "경쟁사", "근거", "조사", "research", "깊이")
        ):
            return "complex"
        if route == "conversation":
            return "simple"
        return "adaptive"

    @staticmethod
    def _select_skill(route: str, message: str) -> str:
        normalized = message.casefold()
        if route == "brand":
            if any(keyword in normalized for keyword in ("포지셔닝", "positioning")):
                return "generate_positioning"
            if any(keyword in normalized for keyword in ("이름", "네이밍", "후보", "초안")):
                return "generate_brand_candidates"
            if any(keyword in normalized for keyword in ("스토리", "브랜드 철학", "미션", "비전")):
                return "generate_brand_philosophy"
        if route == "customer":
            if any(keyword in normalized for keyword in ("여정", "journey", "퍼널")):
                return "generate_customer_journey"
            if any(keyword in normalized for keyword in ("페르소나", "persona")):
                return "generate_persona"
        if route == "business":
            return "generate_business_model"
        if route == "visual":
            if any(keyword in normalized for keyword in ("로고", "logo")):
                return "generate_logo_identity"
            if any(keyword in normalized for keyword in ("캐릭터", "character")):
                return "generate_character_guide"
            return "generate_visual_identity"
        return route
