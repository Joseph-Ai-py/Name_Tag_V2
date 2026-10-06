from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, Field


AgentMode = Literal["simple", "adaptive", "complex"]


class AgentDecision(BaseModel):
    action: Literal["tool_call", "final", "replan"]
    reason: str = Field(min_length=1, max_length=500)
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)


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
    completed_steps: list[str] = field(default_factory=list)
    pending_steps: list[str] = field(default_factory=list)
    tool_results: dict[str, Any] = field(default_factory=dict)
    evaluations: list[dict[str, Any]] = field(default_factory=list)
    status: str = "running"

    def as_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "mode": self.mode,
            "route": self.route,
            "budget": self.budget.model_dump(),
            "iteration": self.iteration,
            "llm_calls": self.llm_calls,
            "completed_steps": self.completed_steps,
            "pending_steps": self.pending_steps,
            "tool_results": self.tool_results,
            "evaluations": self.evaluations,
            "status": self.status,
        }