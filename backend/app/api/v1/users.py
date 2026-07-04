from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.crud import user as crud_user
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut

router = APIRouter()


@router.get("/users", response_model=dict)
def list_users(
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    users = crud_user.get_list(db)
    return {"items": [UserOut.model_validate(u) for u in users], "total": len(users)}


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    if crud_user.get_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    return UserOut.model_validate(crud_user.create(db, data))


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserOut.model_validate(crud_user.update(db, user, data))
