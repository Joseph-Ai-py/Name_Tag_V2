from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageCreateRequest,
    MessageResponse,
)
from app.services.brand_service import get_brand_membership
from app.services.conversation_service import (
    create_conversation,
    delete_conversation,
    create_message,
    get_brand_conversations,
    get_conversation,
    get_messages,
)

router = APIRouter(tags=["conversations"])


def conversation_response(conversation) -> ConversationResponse:
    return ConversationResponse(
        id=conversation.id,
        brand_id=conversation.brand_id,
        created_by=conversation.created_by,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


def message_response(message) -> MessageResponse:
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        artifact=message.artifact,
        created_at=message.created_at,
    )


@router.post(
    "/api/brands/{brand_id}/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation_endpoint(
    brand_id: str,
    payload: ConversationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    if get_brand_membership(db, brand_id, current_user.id) is None:
        raise HTTPException(status_code=404, detail="Brand not found")

    conversation = create_conversation(
        db=db,
        brand_id=brand_id,
        user_id=current_user.id,
        title=payload.title,
    )
    return conversation_response(conversation)


@router.get(
    "/api/brands/{brand_id}/conversations",
    response_model=list[ConversationResponse],
)
def list_conversations_endpoint(
    brand_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    if get_brand_membership(db, brand_id, current_user.id) is None:
        raise HTTPException(status_code=404, detail="Brand not found")

    return [
        conversation_response(item)
        for item in get_brand_conversations(db, brand_id)
    ]


def get_accessible_conversation(
    db: Session,
    conversation_id: str,
    current_user: User,
):
    conversation = get_conversation(db, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if get_brand_membership(db, conversation.brand_id, current_user.id) is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get(
    "/api/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation_endpoint(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    return conversation_response(
        get_accessible_conversation(db, conversation_id, current_user)
    )


@router.post(
    "/api/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message_endpoint(
    conversation_id: str,
    payload: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    conversation = get_accessible_conversation(db, conversation_id, current_user)
    message = create_message(
        db=db,
        conversation=conversation,
        role=payload.role,
        content=payload.content,
        artifact=payload.artifact,
    )
    return message_response(message)


@router.get(
    "/api/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def list_messages_endpoint(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    conversation = get_accessible_conversation(db, conversation_id, current_user)
    return [
        message_response(item)
        for item in get_messages(db, conversation.id)
    ]


@router.delete(
    "/api/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation_endpoint(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    conversation = get_accessible_conversation(db, conversation_id, current_user)
    delete_conversation(db, conversation)