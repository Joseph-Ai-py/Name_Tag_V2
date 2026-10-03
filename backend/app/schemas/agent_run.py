from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ToolCallResponse(BaseModel):
    id: str
    tool_name: str
    status: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    created_at: datetime


class AgentRunResponse(BaseModel):
    id: str
    user_id: str
    brand_id: str
    conversation_id: str | None
    route: str
    message: str
    status: str
    context: dict[str, Any]
    result: dict[str, Any]
    created_at: datetime
    completed_at: datetime | None
    tool_calls: list[ToolCallResponse]
