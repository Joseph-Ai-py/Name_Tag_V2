from typing import Any

from pydantic import BaseModel, Field

from app.schemas.artifact import ArtifactResponse


class AgentChatRequest(BaseModel):
	brand_id: str
	conversation_id: str | None = None
	message: str = Field(min_length=1, max_length=100000)


class AgentChatResponse(BaseModel):
	conversation_id: str
	route: str
	message: str
	artifact: ArtifactResponse | None = None
	proposal_id: str | None = None
	proposal: dict[str, Any] | None = None
	research_job: dict[str, Any] | None = None
	context: dict[str, Any] = {}
	agent: dict[str, Any] = {}
	execution: dict[str, Any] = {}
