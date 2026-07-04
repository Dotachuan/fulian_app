from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class NoticeBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    published_at: Optional[date] = None
    status: str = "published"
    is_pinned: bool = False
    sort_order: int = 0


class NoticeCreate(NoticeBase):
    pass


class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    published_at: Optional[date] = None
    status: Optional[str] = None
    is_pinned: Optional[bool] = None
    sort_order: Optional[int] = None


class NoticeOut(NoticeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoticePublicOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    published_at: Optional[date] = None
    is_pinned: bool

    model_config = {"from_attributes": True}


class PageNotice(BaseModel):
    items: list[NoticeOut]
    total: int
