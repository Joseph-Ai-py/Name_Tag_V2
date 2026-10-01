from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ArtifactCreateRequest(BaseModel):
	type: str = Field(min_length=1, max_length=50)
	title: str = Field(min_length=1, max_length=300)
	content: dict[str, Any]


class ArtifactResponse(BaseModel):
	id: str
	brand_id: str
	created_by: str
	type: str
	title: str
	content: dict[str, Any]
	status: str
	created_at: datetime
	updated_at: datetime
