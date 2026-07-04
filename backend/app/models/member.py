from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    work_unit: Mapped[str] = mapped_column(String(255), nullable=True)
    resident_city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    donor_id: Mapped[int | None] = mapped_column(ForeignKey("donors.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    binding_status: Mapped[str] = mapped_column(String(20), nullable=False, default="unbound")
    binding_source: Mapped[str] = mapped_column(String(20), nullable=False, default="auto")
    note: Mapped[str | None] = mapped_column(String(512), nullable=True)

    default_invoice_title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    default_invoice_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    default_invoice_email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    default_invoice_identity_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    default_invoice_remark: Mapped[str | None] = mapped_column(String(512), nullable=True)

    first_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    donor = relationship("Donor", foreign_keys=[donor_id])


class MemberLoginCode(Base):
    __tablename__ = "member_login_codes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class MemberBindingCode(Base):
    __tablename__ = "member_binding_codes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False, index=True)
    donor_id: Mapped[int] = mapped_column(ForeignKey("donors.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    member = relationship("Member")
    donor = relationship("Donor")
