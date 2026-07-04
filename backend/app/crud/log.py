from typing import Optional
from sqlalchemy.orm import Session

from app.models.log import Log


def add(
    db: Session,
    user_id: Optional[int],
    username: Optional[str],
    action: str,
    module: str,
    target_id: Optional[int] = None,
    detail: Optional[str] = None,
):
    log = Log(
        user_id=user_id,
        username=username,
        action=action,
        module=module,
        target_id=target_id,
        detail=detail,
    )
    db.add(log)
    db.commit()


def get_list(
    db: Session,
    action: str = "",
    date_from=None,
    date_to=None,
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(Log)
    if action:
        q = q.filter(Log.action == action)
    if date_from:
        q = q.filter(Log.created_at >= date_from)
    if date_to:
        q = q.filter(Log.created_at <= date_to)
    total = q.count()
    items = q.order_by(Log.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_by_target(db: Session, module: str, target_id: int) -> list[Log]:
    return (
        db.query(Log)
        .filter_by(module=module, target_id=target_id)
        .order_by(Log.id.desc())
        .all()
    )
