from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class ResearchSourceInput(BaseModel):
	url: HttpUrl
	title: str = Field(min_length=1, max_length=300)
	publisher: str | None = Field(default=None, max_length=200)
	summary: str | None = None
	source_type: str = Field(default="unknown", max_length=30)


class QuickResearchRequest(BaseModel):
	brand_id: str
	query: str = Field(min_length=1, max_length=2000)
	title: str | None = Field(default=None, max_length=300)
	sources: list[ResearchSourceInput] = Field(default_factory=list, max_length=20)


class ResearchPlanRequest(BaseModel):
	brand_id: str
	query: str = Field(min_length=1, max_length=2000)


class ResearchPlanResponse(BaseModel):
	title: str
	objective: str
	questions: list[str]
	scope: list[str]
	output_type: str


class DeepResearchJobRequest(BaseModel):
	brand_id: str
	query: str = Field(min_length=1, max_length=2000)
	plan: ResearchPlanResponse


class ResearchJobResponse(BaseModel):
	id: str
	brand_id: str
	created_by: str
	mode: str
	status: str
	query: str
	plan: dict[str, Any]
	progress: dict[str, Any]
	created_at: datetime
	updated_at: datetime


class ResearchSourceResponse(BaseModel):
	id: str
	url: str
	title: str
	publisher: str | None
	summary: str | None
	source_type: str
	accessed_at: datetime


class ResearchFindingResponse(BaseModel):
	id: str
	statement: str
	evidence: str
	source_ids: list[str]
	confidence: str
	suggested_fields: list[str]
	applied: bool
	created_at: datetime


class ResearchReportResponse(BaseModel):
	id: str
	research_job_id: str
	brand_id: str
	title: str
	executive_summary: str
	sections: list[dict[str, Any]]
	status: str
	sources: list[ResearchSourceResponse]
	findings: list[ResearchFindingResponse]
	created_at: datetime
	updated_at: datetime


class FindingProposalResponse(BaseModel):
	proposal_id: str
	finding_id: str
	base_state_version: int
	status: str


class QuickResearchResponse(BaseModel):
	job: ResearchJobResponse
	report: ResearchReportResponse
