from typing import Optional

from sqlalchemy.orm import Session

from app.models.notice import Notice
from app.schemas.notice import NoticeCreate, NoticeUpdate


def get_list(db: Session, title: str = "", status: str = "", page: int = 1, page_size: int = 20):
    q = db.query(Notice)
    if title:
        q = q.filter(Notice.title.like(f"%{title}%"))
    if status:
        q = q.filter(Notice.status == status)
    total = q.count()
    items = (
        q.order_by(Notice.is_pinned.desc(), Notice.sort_order.asc(), Notice.published_at.desc(), Notice.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_public_list(db: Session, page: int = 1, page_size: int = 10):
    q = db.query(Notice).filter(Notice.status == "published")
    total = q.count()
    items = (
        q.order_by(Notice.is_pinned.desc(), Notice.sort_order.asc(), Notice.published_at.desc(), Notice.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get(db: Session, notice_id: int) -> Optional[Notice]:
    return db.get(Notice, notice_id)


def create(db: Session, data: NoticeCreate) -> Notice:
    item = Notice(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update(db: Session, item: Notice, data: NoticeUpdate) -> Notice:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, item: Notice) -> None:
    db.delete(item)
    db.commit()
