from dataclasses import dataclass, field
from typing import Any, Callable

from sqlalchemy.orm import Session


ToolHandler = Callable[..., Any]


@dataclass(frozen=True)
class ToolContext:
	db: Session
	user_id: str
	brand_id: str
	role: str


@dataclass(frozen=True)
class ToolDefinition:
	name: str
	permission: str
	handler: ToolHandler | None = None
	description: str = ""
	input_schema: dict[str, Any] = field(default_factory=dict)
	output_schema: dict[str, Any] = field(default_factory=dict)
	category: str = "general"
	cost: int = 1
	risk_level: str = "low"
