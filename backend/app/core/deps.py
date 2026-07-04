from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.core.security import decode_token
from app.models.member import Member
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
member_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/member-auth/login")


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(token)
    user_id: int = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 无效")
    user = db.get(User, int(user_id))
    if not user or user.status != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    return user


def require_roles(*roles: str):
    """角色鉴权依赖工厂"""
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限执行此操作")
        return current_user
    return checker


def get_current_member(
    token: str = Depends(member_oauth2_scheme),
    db: Session = Depends(get_db),
) -> Member:
    payload = decode_token(token)
    if payload.get("token_type") != "member":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Member token invalid")
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Member token invalid")
    try:
        member_id = int(str(subject).split(":")[-1])
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Member token invalid")

    member = db.get(Member, member_id)
    if not member or member.status != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Member not found or inactive")
    return member
