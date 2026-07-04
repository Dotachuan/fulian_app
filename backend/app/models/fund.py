from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Fund(Base):
    __tablename__ = "funds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="sub")
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    sort_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    records: Mapped[list["FundUsageRecord"]] = relationship(
        "FundUsageRecord",
        back_populates="fund",
        cascade="all, delete-orphan",
    )


class FundUsageRecord(Base):
    __tablename__ = "fund_usage_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fund_id: Mapped[int] = mapped_column(ForeignKey("funds.id"), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    project_desc: Mapped[str] = mapped_column(String(255), nullable=False)
    income_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    expense_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    remark: Mapped[str] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    fund: Mapped["Fund"] = relationship("Fund", back_populates="records")

