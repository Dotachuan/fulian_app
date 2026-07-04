from typing import Optional

from sqlalchemy.orm import Session

from app.models.project_link import ProjectLink
from app.schemas.project_link import ProjectLinkCreate, ProjectLinkUpdate


def get_list(
    db: Session,
    title: str = "",
    status: str = "",
    section_key: str = "",
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(ProjectLink)
    if status:
        q = q.filter(ProjectLink.status == status)
    if section_key:
        q = q.filter(ProjectLink.section_key == section_key)
    if title:
        q = q.filter(ProjectLink.title.like(f"%{title}%"))
    total = q.count()
    items = (
        q.order_by(ProjectLink.section_key.asc(), ProjectLink.sort_order.asc(), ProjectLink.published_at.desc(), ProjectLink.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_public_by_section(db: Session, section_key: str, page_size: int = 6):
    q = (
        db.query(ProjectLink)
        .filter(ProjectLink.status == "published")
        .filter(ProjectLink.section_key == section_key)
    )
    items = (
        q.order_by(ProjectLink.sort_order.asc(), ProjectLink.published_at.desc(), ProjectLink.id.desc())
        .limit(page_size)
        .all()
    )
    return items


def get(db: Session, item_id: int) -> Optional[ProjectLink]:
    return db.get(ProjectLink, item_id)


def create(db: Session, data: ProjectLinkCreate) -> ProjectLink:
    item = ProjectLink(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update(db: Session, item: ProjectLink, data: ProjectLinkUpdate) -> ProjectLink:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete(db: Session, item: ProjectLink) -> None:
    db.delete(item)
    db.commit()
