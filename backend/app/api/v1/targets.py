from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_roles
from app.crud import target as crud_target
from app.schemas.target import TargetCreate, TargetUpdate, TargetOut, PageTarget

router = APIRouter()


@router.get("/targets", response_model=PageTarget)
def list_targets(
    status: str = "",
    page: int = 1,
    page_size: int = 100,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    items, total = crud_target.get_list(db, status=status, page=page, page_size=page_size)
    return {"items": items, "total": total}


@router.post("/targets", response_model=TargetOut, status_code=201)
def create_target(
    data: TargetCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    return crud_target.create(db, data)


@router.put("/targets/{target_id}", response_model=TargetOut)
def update_target(
    target_id: int,
    data: TargetUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    t = crud_target.get(db, target_id)
    if not t:
        raise HTTPException(status_code=404, detail="捐款目标不存在")
    return crud_target.update(db, t, data)


@router.delete("/targets/{target_id}", status_code=204)
def delete_target(
    target_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    t = crud_target.get(db, target_id)
    if not t:
        raise HTTPException(status_code=404, detail="捐款目标不存在")
    crud_target.delete(db, t)
