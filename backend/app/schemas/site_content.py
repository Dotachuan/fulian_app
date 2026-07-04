from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SiteContentBase(BaseModel):
    key: str
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    status: str = "published"


class SiteContentUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None


class SiteContentOut(SiteContentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SiteContentPublicOut(BaseModel):
    key: str
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None

    model_config = {"from_attributes": True}
