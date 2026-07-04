from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ProjectLinkBase(BaseModel):
    section_key: str
    title: str
    summary: Optional[str] = None
    image_url: str
    target_url: str
    published_at: Optional[date] = None
    status: str = "published"
    is_featured: bool = True
    sort_order: int = 0


class ProjectLinkCreate(ProjectLinkBase):
    pass


class ProjectLinkUpdate(BaseModel):
    section_key: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    target_url: Optional[str] = None
    published_at: Optional[date] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None


class ProjectLinkOut(ProjectLinkBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectLinkPublicOut(BaseModel):
    id: int
    section_key: str
    title: str
    summary: Optional[str] = None
    image_url: str
    target_url: str
    published_at: Optional[date] = None

    model_config = {"from_attributes": True}


class PageProjectLink(BaseModel):
    items: list[ProjectLinkOut]
    total: int
