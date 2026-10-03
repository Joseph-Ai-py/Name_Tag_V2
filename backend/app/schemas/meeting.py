from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MeetingCreateRequest(BaseModel):
    brand_id: str
    agenda: str = Field(min_length=1, max_length=5000)
    mode: str = Field(default="lite", pattern="^(lite|full)$")


class MeetingOpinionResponse(BaseModel):
    id: str
    employee: str
    skill: str
    opinion: str
    evidence: dict[str, Any]
    agreements: list[str]
    conflicts: list[str]
    created_at: datetime


class MeetingDecisionResponse(BaseModel):
    id: str
    decision: str
    rationale: str
    changes: dict[str, Any]
    proposal_id: str | None
    created_at: datetime


class MeetingResponse(BaseModel):
    id: str
    brand_id: str
    created_by: str
    agenda: str
    mode: str
    status: str
    participants: list[str]
    shared_context: dict[str, Any]
    critic: dict[str, Any]
    created_at: datetime
    completed_at: datetime | None
    opinions: list[MeetingOpinionResponse]
    decision: MeetingDecisionResponse | None
