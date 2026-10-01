from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ConversationCreateRequest(BaseModel):
	title: str | None = Field(default=None, max_length=500)


class ConversationResponse(BaseModel):
	id: str
	brand_id: str
	created_by: str
	title: str | None
	created_at: datetime
	updated_at: datetime


class MessageCreateRequest(BaseModel):
	role: str = Field(pattern="^(user|assistant|system)$")
	content: str = Field(min_length=1, max_length=100000)
	artifact: dict[str, Any] | None = None


class MessageResponse(BaseModel):
	id: str
	conversation_id: str
	role: str
	content: str
	artifact: dict[str, Any] | None
	created_at: datetime
