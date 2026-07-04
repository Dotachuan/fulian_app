from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TargetBase(BaseModel):
    name: str
    description: Optional[str] = None


class TargetCreate(TargetBase):
    pass


class TargetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class TargetOut(TargetBase):
    id: int
    code: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PageTarget(BaseModel):
    items: list[TargetOut]
    total: int
