from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.agent.context_manager import build_context
from app.agent.router import classify_message
from app.agent.state import AgentBudget, AgentDecision, AgentExecutionState
from app.llm.schemas import LLMResponse
from app.models.user import User
from app.models.agent_run import AgentRun
from app.models.tool_call import ToolCall
from app.skills.executor import SkillExecutor
from app.skills.registry import skill_registry
from app.services.artifact_service import create_artifact
from app.services.brand_service import get_brand_membership
from app.services.brand_state_service import get_brand_state
from app.services.conversation_service import (
    create_conversation,
    create_message,
    get_conversation,
    get_messages,
)
from app.services.usage_service import record_usage, start_usage
from app.services.proposal_service import create_proposal
from app.tools.base import ToolContext
from app.tools.executor import ToolExecutor
from app.tools.registry import tool_registry

DEFAULT_BUDGET = AgentBudget(max_iterations=5, max_tool_calls=8, max_llm_calls=3)


def _build_execution_plan(route: str, message: str) -> dict[str, Any]:
    normalized = message.casefold()
    positioning_request = route == "brand" and any(
        keyword in normalized for keyword in ("포지셔닝", "positioning", "개선")
    )
    complex_signal = any(
        keyword in normalized
        for keyword in ("전면", "시장", "경쟁사", "근거", "조사", "research", "깊이")
    )
    needs_research = route == "research" or (positioning_request and complex_signal)
    needs_meeting = positioning_request
    required_tools = ["get_brand_state", "get_brand_context"]
    if needs_research:
        required_tools.append("create_research_job")
        required_tools.append("get_research_job")
    if needs_meeting:
        required_tools.append("run_employee_meeting")
    return {
        "goal": message,
        "route": route,
        "needs_research": needs_research,
        "needs_meeting": needs_meeting,
        "required_tools": required_tools,
    }


def _select_next_tool(plan: dict[str, Any], executed_tools: list[str]) -> str | None:
    for tool_name in plan["required_tools"]:
        if tool_name not in executed_tools:
            return tool_name
    return None


def _evaluate_progress(plan: dict[str, Any], executed_tools: list[str]) -> dict[str, Any]:
    missing_tools = [
        tool_name for tool_name in plan["required_tools"] if tool_name not in executed_tools
    ]
    return {
        "sufficient": not missing_tools,
        "missing_tools": missing_tools,
        "reason": "필수 실행 단계가 모두 완료되었습니다." if not missing_tools else "필수 실행 단계가 남아 있습니다.",
    }


def _classify_mode(route: str, plan: dict[str, Any]) -> str:
    if plan["needs_research"] and plan["needs_meeting"]:
        return "complex"
    if route == "conversation" and not plan["required_tools"]:
        return "simple"
    return "adaptive"


def _resolve_route(message: str) -> str:
    route = classify_message(message)
    normalized = message.casefold()
    if any(keyword in normalized for keyword in ("포지셔닝", "positioning")):
        return "brand"
    return route


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
        return route
    if route == "business":
        return "generate_business_model"
    if route == "visual":
        if any(keyword in normalized for keyword in ("로고", "logo")):
            return "generate_logo_identity"
        if any(keyword in normalized for keyword in ("캐릭터", "character")):
            return "generate_character_guide"
        return "generate_visual_identity"
    return route


def _available_tools(role: str) -> list[dict[str, Any]]:
    definitions = []
    for name in tool_registry.names():
        definition = tool_registry.get(name)
        try:
            from app.agent.permissions import can_use_tool

            available = can_use_tool(role, definition.permission)
        except ValueError:
            available = False
        if available:
            definitions.append(
                {
                    "name": definition.name,
                    "description": definition.description,
                    "category": definition.category,
                    "permission": definition.permission,
                    "risk_level": definition.risk_level,
                }
            )
    return definitions


def _manager_decide(
    state: AgentExecutionState,
    plan: dict[str, Any],
    role: str,
    message: str,
) -> AgentDecision:
    if state.pending_steps:
        next_tool = state.pending_steps[0]
        definition = tool_registry.get(next_tool)
        if any(item["name"] == next_tool for item in _available_tools(role)):
            arguments: dict[str, Any] = {"task": state.route}
            if next_tool == "run_employee_meeting":
                arguments = {"agenda": message, "mode": "full" if state.mode == "complex" else "lite"}
            elif next_tool == "create_research_job":
                arguments = {"query": message}
            elif next_tool == "get_research_job":
                job_result = state.tool_results.get("create_research_job", {})
                arguments = {"job_id": job_result.get("job_id", "")}
            return AgentDecision(
                action="tool_call",
                tool_name=next_tool,
                arguments=arguments,
                reason=f"{definition.category} 맥락이 필요합니다.",
            )
        return AgentDecision(
            action="replan",
            reason=f"현재 권한으로 {next_tool}을 사용할 수 없어 남은 단계를 조정합니다.",
        )
    return AgentDecision(action="final", reason="현재 실행 결과로 응답을 생성할 수 있습니다.")


def run_agent(
    db: Session,
    current_user: User,
    brand_id: str,
    conversation_id: str | None,
    message: str,
) -> dict[str, Any]:
    started_at = start_usage()
    membership = get_brand_membership(db, brand_id, current_user.id)
    if membership is None:
        raise ValueError("Brand not found")

    brand_state = get_brand_state(db, brand_id)
    context = build_context(brand_state.state if brand_state else None)

    if conversation_id:
        conversation = get_conversation(db, conversation_id, brand_id)
        if conversation is None:
            raise ValueError("Conversation not found")
    else:
        conversation = create_conversation(
            db=db,
            brand_id=brand_id,
            user_id=current_user.id,
            title=message[:100],
        )

    history = [
        {"role": item.role, "content": item.content}
        for item in get_messages(db, conversation.id)
    ]
    context["conversation_history"] = history
    create_message(db, conversation, "user", message, None)

    route = _resolve_route(message)
    agent_run = AgentRun(
        user_id=current_user.id,
        brand_id=brand_id,
        conversation_id=conversation.id,
        route=route,
        message=message,
        status="running",
        context=context,
        result={},
    )
    db.add(agent_run)
    db.flush()
    tool_context = ToolContext(
        db=db,
        user_id=current_user.id,
        brand_id=brand_id,
        role=membership.role,
    )
    plan = _build_execution_plan(route, message)
    mode = _classify_mode(route, plan)
    execution = AgentExecutionState(
        goal=message,
        mode=mode,
        route=route,
        budget=DEFAULT_BUDGET.model_copy(deep=True),
        pending_steps=list(plan["required_tools"]),
    )
    context["execution_plan"] = plan
    context["available_tools"] = _available_tools(membership.role)
    context["available_skills"] = [
        {
            "name": name,
            "description": skill_registry.get(name).description,
            "required_context": skill_registry.get(name).required_context,
            "output_paths": skill_registry.get(name).output_paths,
        }
        for name in skill_registry.names()
    ]
    context["agent_state"] = execution.as_dict()
    executed_tools: list[str] = []
    for _ in range(execution.budget.max_iterations):
        execution.iteration += 1
        decision = _manager_decide(execution, plan, membership.role, message)
        if decision.action == "final":
            break
        if decision.action == "replan":
            execution.pending_steps.pop(0)
            execution.evaluations.append({"decision": decision.model_dump()})
            continue
        if execution.llm_calls > execution.budget.max_llm_calls:
            execution.status = "budget_exceeded"
            break
        if len(executed_tools) >= execution.budget.max_tool_calls:
            execution.status = "budget_exceeded"
            break
        tool_name = decision.tool_name
        if tool_name is None:
            break
        tool_arguments = decision.arguments
        try:
            tool_result = ToolExecutor().execute(tool_name, tool_context, **tool_arguments)
            execution.tool_results[tool_name] = tool_result
            db.add(ToolCall(agent_run_id=agent_run.id, tool_name=tool_name, status="completed", arguments=tool_arguments, result=tool_result))
        except Exception as exc:
            db.add(ToolCall(agent_run_id=agent_run.id, tool_name=tool_name, status="failed", arguments=tool_arguments, result={"error": str(exc)}))
            execution.status = "degraded"
            execution.evaluations.append({"tool": tool_name, "status": "failed", "error": str(exc)})
        executed_tools.append(tool_name)
        execution.completed_steps.append(tool_name)
        execution.pending_steps = [item for item in execution.pending_steps if item != tool_name]
        execution.evaluations.append(_evaluate_progress(plan, executed_tools))
        context["agent_state"] = execution.as_dict()
    if execution.pending_steps and execution.status == "running" and execution.iteration >= execution.budget.max_iterations:
        execution.status = "budget_exceeded"
    context["tool_results"] = execution.tool_results
    context["evaluations"] = execution.evaluations
    context["final_evaluation"] = _evaluate_progress(plan, executed_tools)

    execution.llm_calls += 1
    skill_name = _select_skill(route, message)
    context["selected_skill"] = skill_name
    try:
        llm_response = SkillExecutor().execute(skill_name=skill_name, message=message, context=context)
    except Exception as exc:
        execution.status = "degraded"
        llm_response = LLMResponse(text="요청을 처리하는 동안 일부 단계가 실패했습니다. 실행 기록을 확인해 주세요.")
        context["llm_error"] = str(exc)
    record_usage(db, current_user.id, brand_id, "chat", started_at)

    artifact = None
    proposal_id = None
    proposal_error = None
    meeting_result = execution.tool_results.get("run_employee_meeting")
    if isinstance(meeting_result, dict):
        proposal_id = meeting_result.get("proposal_id")
    if llm_response.proposed_changes and proposal_id is None:
        try:
            proposal = create_proposal(
                db=db,
                brand_id=brand_id,
                user_id=current_user.id,
                title=f"{route.title()} 제안",
                summary=llm_response.text,
                changes=llm_response.proposed_changes,
            )
            proposal_id = proposal.id
        except ValueError as exc:
            proposal_error = str(exc)
            context["proposal_error"] = proposal_error
    if llm_response.artifact_type is not None:
        artifact = create_artifact(
            db=db,
            brand_id=brand_id,
            user_id=current_user.id,
            artifact_type=llm_response.artifact_type,
            title=llm_response.artifact_type.replace("_", " ").title(),
            content=llm_response.artifact_content,
        )

    create_message(
        db=db,
        conversation=conversation,
        role="assistant",
        content=llm_response.text,
        artifact={"artifact_id": artifact.id} if artifact else None,
    )
    final_status = execution.status if execution.status != "running" else "completed"
    agent_run.status = final_status
    agent_run.context = context
    agent_run.result = {
        "route": route,
        "mode": mode,
        "status": final_status,
        "iterations": execution.iteration,
        "tools_used": executed_tools,
        "llm_calls": execution.llm_calls,
        "proposal_id": proposal_id,
        "proposal_error": proposal_error,
        "artifact_id": artifact.id if artifact else None,
    }
    agent_run.completed_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "conversation_id": conversation.id,
        "run_id": agent_run.id,
        "route": route,
        "message": llm_response.text,
        "artifact": artifact,
        "proposal_id": proposal_id,
        "context": context,
        "execution": {
            "mode": mode,
            "status": final_status,
            "iterations": execution.iteration,
            "tools_used": executed_tools,
        },
    }