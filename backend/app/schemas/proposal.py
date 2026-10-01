from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProposalCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    summary: str = Field(min_length=1, max_length=5000)
    changes: dict[str, Any]


class ProposalResponse(BaseModel):
    id: str
    brand_id: str
    created_by: str
    title: str
    summary: str
    changes: dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime