from dataclasses import dataclass
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
