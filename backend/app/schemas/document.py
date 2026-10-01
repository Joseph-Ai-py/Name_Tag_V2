from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentCreateRequest(BaseModel):
	title: str = Field(min_length=1, max_length=300)


class DocumentUpdateRequest(BaseModel):
	title: str = Field(min_length=1, max_length=300)


class BlockCreateRequest(BaseModel):
	type: str = Field(min_length=1, max_length=50)
	content: dict[str, Any] = Field(default_factory=dict)
	position: int = Field(default=0, ge=0)


class BlockUpdateRequest(BaseModel):
	content: dict[str, Any]


class BlockResponse(BaseModel):
	id: str
	document_id: str
	type: str
	content: dict[str, Any]
	position: int
	created_at: datetime
	updated_at: datetime


class DocumentResponse(BaseModel):
	id: str
	brand_id: str
	created_by: str
	title: str
	blocks: list[BlockResponse]
	created_at: datetime
	updated_at: datetime
