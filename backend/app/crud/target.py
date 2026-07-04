from typing import Optional
from sqlalchemy.orm import Session

from app.models.target import Target
from app.schemas.target import TargetCreate, TargetUpdate


def _next_code(db: Session) -> str:
    count = db.query(Target).count()
    return f"TGT{count + 1:04d}"


def get_list(db: Session, status: str = "", page: int = 1, page_size: int = 100):
    q = db.query(Target).filter(Target.is_deleted == False)
    if status:
        q = q.filter(Target.status == status)
    total = q.count()
    items = q.order_by(Target.id).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get(db: Session, target_id: int) -> Optional[Target]:
    return db.query(Target).filter_by(id=target_id, is_deleted=False).first()


def create(db: Session, data: TargetCreate) -> Target:
    target = Target(code=_next_code(db), **data.model_dump())
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


def update(db: Session, target: Target, data: TargetUpdate) -> Target:
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(target, k, v)
    db.commit()
    db.refresh(target)
    return target


def delete(db: Session, target: Target):
    target.is_deleted = True
    db.commit()
