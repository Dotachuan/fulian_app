from typing import Optional

from sqlalchemy.orm import Session

from app.models.news import NewsPost
from app.schemas.news import NewsPostCreate, NewsPostUpdate


def get_list(
    db: Session,
    status: str = "",
    title: str = "",
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(NewsPost)
    if status:
        q = q.filter(NewsPost.status == status)
    if title:
        q = q.filter(NewsPost.title.like(f"%{title}%"))
    total = q.count()
    items = (
        q.order_by(NewsPost.sort_order.asc(), NewsPost.published_at.desc(), NewsPost.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_public_list(
    db: Session,
    featured_only: bool = False,
    page: int = 1,
    page_size: int = 6,
):
    q = db.query(NewsPost).filter(NewsPost.status == "published")
    if featured_only:
        q = q.filter(NewsPost.is_featured == True)
    total = q.count()
    items = (
        q.order_by(NewsPost.sort_order.asc(), NewsPost.published_at.desc(), NewsPost.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get(db: Session, news_id: int) -> Optional[NewsPost]:
    return db.get(NewsPost, news_id)


def create(db: Session, data: NewsPostCreate) -> NewsPost:
    item = NewsPost(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update(db: Session, item: NewsPost, data: NewsPostUpdate) -> NewsPost:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, item: NewsPost) -> None:
    db.delete(item)
    db.commit()
