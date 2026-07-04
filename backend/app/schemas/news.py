from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class NewsPostBase(BaseModel):
    title: str
    summary: Optional[str] = None
    cover_url: Optional[str] = None
    source_url: str
    source: str = "微信公众号"
    published_at: Optional[date] = None
    status: str = "published"
    is_featured: bool = True
    sort_order: int = 0


class NewsPostCreate(NewsPostBase):
    pass


class NewsPostUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    cover_url: Optional[str] = None
    source_url: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[date] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None


class NewsPostOut(NewsPostBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NewsPostPublicOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    cover_url: Optional[str] = None
    source_url: str
    source: str
    published_at: Optional[date] = None

    model_config = {"from_attributes": True}


class PageNewsPost(BaseModel):
    items: list[NewsPostOut]
    total: int
