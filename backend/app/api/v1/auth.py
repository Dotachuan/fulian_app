from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.security import verify_password, create_access_token
from app.crud import user as crud_user
from app.schemas.user import LoginForm, Token, UserOut

router = APIRouter()


@router.post("/auth/login", response_model=Token)
def login(form: LoginForm, db: Session = Depends(get_db)):
    user = crud_user.get_by_username(db, form.username)
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已禁用")
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/auth/logout")
def logout(current_user=Depends(get_current_user)):
    # JWT 无状态，前端清除 token 即可
    return {"message": "已退出登录"}
