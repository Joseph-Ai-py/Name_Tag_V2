from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    format: str = Field(default="json", pattern="^json$")


class ExportResponse(BaseModel):
    format: str
    exported_at: datetime
    brand: dict[str, Any]
    brand_state: dict[str, Any]
    artifacts: list[dict[str, Any]]
    assets: list[dict[str, Any]]
    research: list[dict[str, Any]]