from datetime import datetime

from pydantic import BaseModel, Field


class BrandCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)


class BrandUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)


class BrandResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class BrandListItem(BaseModel):
    id: str
    name: str
    description: str | None
    role: str
    created_at: datetime
    updated_at: datetime