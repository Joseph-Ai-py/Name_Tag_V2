from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SnapshotResponse(BaseModel):
    id: str
    brand_id: str
    version: int
    state: dict[str, Any]
    created_by: str
    created_at: datetime
