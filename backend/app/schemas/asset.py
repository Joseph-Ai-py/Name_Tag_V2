from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AssetCreateRequest(BaseModel):
	type: str = Field(min_length=1, max_length=50)
	filename: str = Field(min_length=1, max_length=300)
	mime_type: str = Field(min_length=1, max_length=100)
	storage_path: str = Field(min_length=1, max_length=2000)
	metadata: dict[str, Any] = Field(default_factory=dict)


class AssetResponse(BaseModel):
	id: str
	brand_id: str
	created_by: str
	type: str
	filename: str
	mime_type: str
	storage_path: str
	metadata: dict[str, Any]
	created_at: datetime
