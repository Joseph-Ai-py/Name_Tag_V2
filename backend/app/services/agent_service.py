from typing import Any

from sqlalchemy.orm import Session

from app.agent.context_manager import build_context
from app.agent.router import classify_message
from app.models.user import User
from app.skills.executor import SkillExecutor
from app.services.artifact_service import create_artifact
from app.services.brand_state_service import get_brand_state
from app.services.conversation_service import (
    create_conversation,
    create_message,
    get_conversation,
    get_messages,
)
from app.services.usage_service import record_usage, start_usage


def run_agent(
    db: Session,
    current_user: User,
    brand_id: str,
    conversation_id: str | None,
    message: str,
) -> dict[str, Any]:
    started_at = start_usage()
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
    llm_response = SkillExecutor().execute(
        skill_name=route,
        message=message,
        context=context,
    )
    record_usage(db, current_user.id, brand_id, "chat", started_at)

    artifact = None
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

    return {
        "conversation_id": conversation.id,
        "route": route,
        "message": llm_response.text,
        "artifact": artifact,
        "context": context,
    }