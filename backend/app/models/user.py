from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="operator")
    # admin / operator / reviewer / viewer
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    # active / inactive
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
