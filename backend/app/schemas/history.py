from datetime import datetime
from typing import Any

from pydantic import BaseModel


class HistoryResponse(BaseModel):
    id: str
    brand_id: str
    user_id: str
    action: str
    proposal_id: str | None
    details: dict[str, Any]
    created_at: datetime