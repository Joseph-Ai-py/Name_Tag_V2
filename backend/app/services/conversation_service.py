from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message


def create_conversation(
	db: Session,
	brand_id: str,
	user_id: str,
	title: str | None,
) -> Conversation:
	conversation = Conversation(
		brand_id=brand_id,
		created_by=user_id,
		title=title.strip() if title else None,
	)
	db.add(conversation)
	db.commit()
	db.refresh(conversation)
	return conversation


def get_brand_conversations(
	db: Session,
	brand_id: str,
) -> list[Conversation]:
	result = db.execute(
		select(Conversation)
		.where(Conversation.brand_id == brand_id)
		.order_by(Conversation.created_at.desc())
	)
	return list(result.scalars().all())


def get_conversation(
	db: Session,
	conversation_id: str,
	brand_id: str | None = None,
) -> Conversation | None:
	query = select(Conversation).where(Conversation.id == conversation_id)
	if brand_id is not None:
		query = query.where(Conversation.brand_id == brand_id)
	return db.execute(query).scalar_one_or_none()


def create_message(
	db: Session,
	conversation: Conversation,
	role: str,
	content: str,
	artifact: dict | None,
) -> Message:
	message = Message(
		conversation_id=conversation.id,
		role=role,
		content=content,
		artifact=artifact,
	)
	db.add(message)
	db.commit()
	db.refresh(message)
	return message


def get_messages(
	db: Session,
	conversation_id: str,
) -> list[Message]:
	result = db.execute(
		select(Message)
		.where(Message.conversation_id == conversation_id)
		.order_by(Message.created_at.asc())
	)
	return list(result.scalars().all())
