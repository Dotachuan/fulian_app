from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LogOut(BaseModel):
    id: int
    username: Optional[str]
    action: str
    module: str
    detail: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class PageLog(BaseModel):
    items: list[LogOut]
    total: int
