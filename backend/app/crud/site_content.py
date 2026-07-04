from typing import Optional

from sqlalchemy.orm import Session

from app.models.site_content import SiteContent
from app.schemas.site_content import SiteContentUpdate


def list_all(db: Session):
    return db.query(SiteContent).order_by(SiteContent.id.asc()).all()


def list_public(db: Session):
    return db.query(SiteContent).filter(SiteContent.status == "published").order_by(SiteContent.id.asc()).all()


def get_by_key(db: Session, key: str) -> Optional[SiteContent]:
    return db.query(SiteContent).filter(SiteContent.key == key).first()


def update(db: Session, item: SiteContent, data: SiteContentUpdate) -> SiteContent:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item
