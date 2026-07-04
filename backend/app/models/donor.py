from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Donor(Base):
    __tablename__ = "donors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="person")
    # person / company
    phone: Mapped[str] = mapped_column(String(32), nullable=True)
    email: Mapped[str] = mapped_column(String(128), nullable=True)
    address: Mapped[str] = mapped_column(String(256), nullable=True)
    id_no: Mapped[str] = mapped_column(String(64), nullable=True)
    remark: Mapped[str] = mapped_column(String(512), nullable=True)
    binding_code: Mapped[str | None] = mapped_column(String(32), nullable=True, unique=True, index=True)
    binding_code_status: Mapped[str | None] = mapped_column(String(20), nullable=True, default=None)
    binding_bound_member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), nullable=True, index=True)
    binding_bound_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    donations: Mapped[list] = relationship("Donation", back_populates="donor")
    binding_member = relationship("Member", foreign_keys=[binding_bound_member_id])
