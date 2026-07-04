from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ParkLinkBase(BaseModel):
    title: str
    summary: Optional[str] = None
    image_url: str
    target_url: str
    published_at: Optional[date] = None
    status: str = "published"
    is_featured: bool = True
    sort_order: int = 0


class ParkLinkCreate(ParkLinkBase):
    pass


class ParkLinkUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    target_url: Optional[str] = None
    published_at: Optional[date] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None


class ParkLinkOut(ParkLinkBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ParkLinkPublicOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    image_url: str
    target_url: str
    published_at: Optional[date] = None

    model_config = {"from_attributes": True}


class PageParkLink(BaseModel):
    items: list[ParkLinkOut]
    total: int
