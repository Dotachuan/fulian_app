from typing import Optional

from sqlalchemy.orm import Session

from app.models.park_link import ParkLink
from app.schemas.park_link import ParkLinkCreate, ParkLinkUpdate


def get_list(
    db: Session,
    title: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(ParkLink)
    if status:
        q = q.filter(ParkLink.status == status)
    if title:
        q = q.filter(ParkLink.title.like(f"%{title}%"))
    total = q.count()
    items = (
        q.order_by(ParkLink.sort_order.asc(), ParkLink.published_at.desc(), ParkLink.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_public_list(
    db: Session,
    featured_only: bool = False,
    page: int = 1,
    page_size: int = 12,
):
    q = db.query(ParkLink).filter(ParkLink.status == "published")
    if featured_only:
        q = q.filter(ParkLink.is_featured == True)
    total = q.count()
    items = (
        q.order_by(ParkLink.sort_order.asc(), ParkLink.published_at.desc(), ParkLink.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get(db: Session, item_id: int) -> Optional[ParkLink]:
    return db.get(ParkLink, item_id)


def create(db: Session, data: ParkLinkCreate) -> ParkLink:
    item = ParkLink(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update(db: Session, item: ParkLink, data: ParkLinkUpdate) -> ParkLink:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, item: ParkLink) -> None:
    db.delete(item)
    db.commit()
