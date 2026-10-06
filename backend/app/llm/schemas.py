from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field

from app.agent.state import AgentDecision


@dataclass(frozen=True)
class LLMResponse:
	text: str
	artifact_type: str | None = None
	artifact_content: dict[str, Any] = field(default_factory=dict)
	proposed_changes: dict[str, Any] | None = None


class LLMPlanResponse(BaseModel):
	action: str
	reason: str = Field(min_length=1, max_length=500)
	tool_name: str | None = None
	arguments: dict[str, Any] = Field(default_factory=dict)
	message: str | None = None
	confidence: float | None = Field(default=None, ge=0, le=1)
	skill_name: str | None = None
	proposal_id: str | None = None
	pending_resource_id: str | None = None

	def to_decision(self) -> AgentDecision:
		return AgentDecision.model_validate(self.model_dump())
