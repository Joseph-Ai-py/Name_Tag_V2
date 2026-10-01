from datetime import datetime
from typing import Any

from pydantic import BaseModel


class BrandStateResponse(BaseModel):
    id: str
    brand_id: str
    state: dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime


class BrandStateUpdateRequest(BaseModel):
    state: dict[str, Any]
    expected_version: int | None = None