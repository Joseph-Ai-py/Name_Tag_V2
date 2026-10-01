from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LLMResponse:
	text: str
	artifact_type: str | None = None
	artifact_content: dict[str, Any] = field(default_factory=dict)
