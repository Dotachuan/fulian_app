from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Date, DateTime, Numeric, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Donation(Base):
    __tablename__ = "donations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    donation_no: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    donation_date: Mapped[date] = mapped_column(Date, nullable=False)

    donor_id: Mapped[int] = mapped_column(ForeignKey("donors.id"), nullable=False)
    target_id: Mapped[int] = mapped_column(ForeignKey("targets.id"), nullable=False)

    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(32), nullable=False, default="bank")
    # cash / bank / alipay / wechat / other

    receipt_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    receipt_no: Mapped[str] = mapped_column(String(64), nullable=True)
    remark: Mapped[str] = mapped_column(String(512), nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    # normal / pending / void

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    donor: Mapped["Donor"] = relationship("Donor", back_populates="donations")
    target: Mapped["Target"] = relationship("Target", back_populates="donations")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    attachments: Mapped[list] = relationship("Attachment", back_populates="donation", cascade="all, delete-orphan")
