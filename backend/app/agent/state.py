from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


AgentMode = Literal["simple", "adaptive", "complex"]


class AgentDecision(BaseModel):
    action: Literal[
        "tool_call",
        "final",
        "ask_user",
        "propose",
        "replan",
        "wait_for_approval",
    ]
    reason: str = Field(min_length=1, max_length=500)
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    message: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    skill_name: str | None = None
    proposal_id: str | None = None
    pending_resource_id: str | None = None
    proposal_title: str | None = None
    proposal_summary: str | None = None
    proposed_changes: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_action_payload(self) -> "AgentDecision":
        if self.action == "tool_call" and not self.tool_name:
            raise ValueError("tool_call requires tool_name")
        if self.action in {"ask_user", "wait_for_approval"} and not self.message:
            raise ValueError(f"{self.action} requires message")
        if self.action == "wait_for_approval" and not (self.proposal_id or self.pending_resource_id):
            raise ValueError("wait_for_approval requires a pending resource")
        if self.action != "tool_call" and self.tool_name is not None:
            raise ValueError("tool_name is only valid for tool_call")
        return self


class AgentBudget(BaseModel):
    max_iterations: int = Field(default=5, ge=1, le=20)
    max_tool_calls: int = Field(default=8, ge=1, le=50)
    max_llm_calls: int = Field(default=3, ge=1, le=20)


@dataclass
class AgentExecutionState:
    goal: str
    mode: AgentMode
    route: str
    budget: AgentBudget = field(default_factory=AgentBudget)
    iteration: int = 0
    llm_calls: int = 0
    tool_calls: int = 0
    completed_steps: list[str] = field(default_factory=list)
    pending_steps: list[str] = field(default_factory=list)
    tool_results: dict[str, Any] = field(default_factory=dict)
    evaluations: list[dict[str, Any]] = field(default_factory=list)
    observations: list[dict[str, Any]] = field(default_factory=list)
    failed_tools: list[str] = field(default_factory=list)
    waiting_for: str | None = None
    pending_resource_id: str | None = None
    base_state_version: int | None = None
    failure_code: str | None = None
    failure_stage: str | None = None
    failure_type: str | None = None
    status: str = "running"

    def as_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "mode": self.mode,
            "route": self.route,
            "budget": self.budget.model_dump(),
            "iteration": self.iteration,
            "llm_calls": self.llm_calls,
            "tool_calls": self.tool_calls,
            "completed_steps": self.completed_steps,
            "pending_steps": self.pending_steps,
            "tool_results": self.tool_results,
            "evaluations": self.evaluations,
            "observations": self.observations,
            "failed_tools": self.failed_tools,
            "waiting_for": self.waiting_for,
            "pending_resource_id": self.pending_resource_id,
            "base_state_version": self.base_state_version,
            "failure_code": self.failure_code,
            "failure_stage": self.failure_stage,
            "failure_type": self.failure_type,
            "status": self.status,
        }