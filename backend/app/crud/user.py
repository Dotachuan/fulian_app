from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


def get_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter_by(username=username).first()


def get_list(db: Session) -> list[User]:
    return db.query(User).order_by(User.id).all()


def create(db: Session, data: UserCreate) -> User:
    user = User(
        username=data.username,
        password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user: User, data: UserUpdate) -> User:
    if data.role is not None:
        user.role = data.role
    if data.status is not None:
        user.status = data.status
    if data.password:
        user.password = hash_password(data.password)
    db.commit()
    db.refresh(user)
    return user
