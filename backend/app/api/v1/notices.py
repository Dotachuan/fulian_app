from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.crud import log as crud_log
from app.crud import notice as crud_notice
from app.models.user import User
from app.schemas.notice import NoticeCreate, NoticeOut, NoticeUpdate, PageNotice

router = APIRouter()


@router.get("/notices", response_model=PageNotice)
def list_notices(
    title: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    items, total = crud_notice.get_list(db, title=title, status=status, page=page, page_size=page_size)
    return {"items": items, "total": total}


@router.post("/notices", response_model=NoticeOut, status_code=201)
def create_notice(
    data: NoticeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = crud_notice.create(db, data)
    crud_log.add(db, current_user.id, current_user.username, "create", "notice", item.id, f"create notice {item.title}")
    return item


@router.put("/notices/{notice_id}", response_model=NoticeOut)
def update_notice(
    notice_id: int,
    data: NoticeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = crud_notice.get(db, notice_id)
    if not item:
        raise HTTPException(status_code=404, detail="notice not found")
    item = crud_notice.update(db, item, data)
    crud_log.add(db, current_user.id, current_user.username, "update", "notice", item.id, f"update notice {item.title}")
    return item


@router.delete("/notices/{notice_id}", status_code=204)
def delete_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    item = crud_notice.get(db, notice_id)
    if not item:
        raise HTTPException(status_code=404, detail="notice not found")
    crud_notice.delete(db, item)
    crud_log.add(db, current_user.id, current_user.username, "delete", "notice", notice_id, f"delete notice {item.title}")
