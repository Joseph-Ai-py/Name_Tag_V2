from typing import Any

from sqlalchemy.orm import Session

from app.models.user import User
from app.llm.gateway import get_llm_gateway
from app.services.artifact_service import create_artifact
from app.services.brand_state_service import get_brand_state
from app.services.conversation_service import (
    create_conversation,
    create_message,
    get_conversation,
)


ROUTE_KEYWORDS = {
    "research": ("조사", "리서치", "시장", "경쟁사", "트렌드"),
    "customer": ("타겟", "고객", "페르소나", "사용자", "pain point"),
    "brand": ("브랜드", "포지셔닝", "스토리", "미션", "톤"),
    "business": ("사업", "문제", "솔루션", "수익", "가격"),
    "visual": ("로고", "색상", "비주얼", "디자인", "타이포"),
}


def classify_message(message: str) -> str:
    normalized = message.casefold()
    for route, keywords in ROUTE_KEYWORDS.items():
        if any(keyword.casefold() in normalized for keyword in keywords):
            return route
    return "conversation"


def build_context(state: dict[str, Any] | None) -> dict[str, Any]:
    if not state:
        return {}

    return {
        "business": state.get("business", {}),
        "customer": state.get("customer", {}),
        "brand": state.get("brand", {}),
        "visual": state.get("visual", {}),
    }


def run_agent(
    db: Session,
    current_user: User,
    brand_id: str,
    conversation_id: str | None,
    message: str,
) -> dict[str, Any]:
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

    create_message(db, conversation, "user", message, None)
    route = classify_message(message)
    llm_response = get_llm_gateway().generate_text(
        task=route,
        message=message,
        context=context,
    )

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