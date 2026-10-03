from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.agent.context_manager import build_context
from app.agent.router import classify_message
from app.models.user import User
from app.models.agent_run import AgentRun
from app.models.tool_call import ToolCall
from app.skills.executor import SkillExecutor
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

MAX_LLM_CALLS = 3
MAX_TOOL_CALLS = 5
MAX_ITERATIONS = 3


def _select_next_tool(route: str, message: str, executed_tools: list[str]) -> str | None:
    if route == "brand" and "get_brand_state" not in executed_tools:
        return "get_brand_state"
    if route == "brand" and "get_brand_context" not in executed_tools:
        return "get_brand_context"
    if route == "brand" and any(keyword in message for keyword in ("포지셔닝", "positioning", "개선")) and "run_employee_meeting" not in executed_tools:
        return "run_employee_meeting"
    if route in {"business", "customer", "visual", "research"} and not executed_tools:
        return "get_brand_context"
    if route == "research" and "create_research_job" not in executed_tools:
        return "create_research_job"
    if route == "conversation" and any(keyword in message.lower() for keyword in ("state", "context", "현황", "맥락")):
        return "get_brand_state"
    return None


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

    route = classify_message(message)
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
    executed_tools: list[str] = []
    tool_results: dict[str, Any] = {}
    for _ in range(MAX_ITERATIONS):
        tool_name = _select_next_tool(route, message, executed_tools)
        if tool_name is None:
            break
        if len(executed_tools) >= MAX_TOOL_CALLS:
            raise RuntimeError("Agent tool call limit exceeded")
        try:
            tool_arguments = {"task": route}
            if tool_name == "run_employee_meeting":
                tool_arguments = {"agenda": message, "mode": "full" if route == "brand" else "lite"}
            elif tool_name == "create_research_job":
                tool_arguments = {"query": message}
            tool_result = ToolExecutor().execute(tool_name, tool_context, **tool_arguments)
            tool_results[tool_name] = tool_result
            db.add(ToolCall(agent_run_id=agent_run.id, tool_name=tool_name, status="completed", arguments=tool_arguments, result=tool_result))
        except Exception as exc:
            db.add(ToolCall(agent_run_id=agent_run.id, tool_name=tool_name, status="failed", arguments=tool_arguments, result={"error": str(exc)}))
            agent_run.status = "failed"
            agent_run.completed_at = datetime.now(timezone.utc)
            db.commit()
            raise
        executed_tools.append(tool_name)
    context["tool_results"] = tool_results

    llm_calls = 1
    if llm_calls > MAX_LLM_CALLS:
        raise RuntimeError("Agent LLM call limit exceeded")

    llm_response = SkillExecutor().execute(
        skill_name=route,
        message=message,
        context=context,
    )
    record_usage(db, current_user.id, brand_id, "chat", started_at)

    artifact = None
    proposal_id = None
    proposal_error = None
    meeting_result = tool_results.get("run_employee_meeting")
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
    agent_run.status = "completed"
    agent_run.context = context
    agent_run.result = {
        "route": route,
        "proposal_id": proposal_id,
        "proposal_error": proposal_error,
        "artifact_id": artifact.id if artifact else None,
    }
    agent_run.completed_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "conversation_id": conversation.id,
        "route": route,
        "message": llm_response.text,
        "artifact": artifact,
        "proposal_id": proposal_id,
        "context": context,
    }