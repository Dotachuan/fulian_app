from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.fund import Fund, FundUsageRecord
from app.schemas.fund import FundCreate, FundUpdate, FundUsageCreate, FundUsageUpdate


def list_funds(db: Session, status: str = "", page: int = 1, page_size: int = 20):
    q = db.query(Fund)
    if status:
        q = q.filter(Fund.status == status)
    total = q.count()
    items = q.order_by(Fund.sort_order.asc(), Fund.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_fund(db: Session, fund_id: int) -> Optional[Fund]:
    return db.get(Fund, fund_id)


def create_fund(db: Session, data: FundCreate) -> Fund:
    fund = Fund(**data.model_dump())
    db.add(fund)
    db.commit()
    db.refresh(fund)
    return fund


def update_fund(db: Session, fund: Fund, data: FundUpdate) -> Fund:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(fund, key, value)
    db.commit()
    db.refresh(fund)
    return fund


def delete_fund(db: Session, fund: Fund) -> None:
    db.delete(fund)
    db.commit()


def list_usage_records(
    db: Session,
    fund_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(FundUsageRecord)
    if fund_id:
        q = q.filter(FundUsageRecord.fund_id == fund_id)
    if date_from:
        q = q.filter(FundUsageRecord.record_date >= date_from)
    if date_to:
        q = q.filter(FundUsageRecord.record_date <= date_to)
    total = q.count()
    items = (
        q.order_by(FundUsageRecord.record_date.desc(), FundUsageRecord.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_usage_record(db: Session, record_id: int) -> Optional[FundUsageRecord]:
    return db.get(FundUsageRecord, record_id)


def create_usage_record(db: Session, data: FundUsageCreate) -> FundUsageRecord:
    record = FundUsageRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_usage_record(db: Session, record: FundUsageRecord, data: FundUsageUpdate) -> FundUsageRecord:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def delete_usage_record(db: Session, record: FundUsageRecord) -> None:
    db.delete(record)
    db.commit()


def fund_totals(db: Session, fund_id: int):
    income, expense = (
        db.query(
            func.coalesce(func.sum(FundUsageRecord.income_amount), 0),
            func.coalesce(func.sum(FundUsageRecord.expense_amount), 0),
        )
        .filter(FundUsageRecord.fund_id == fund_id)
        .one()
    )
    total_income = Decimal(str(income))
    total_expense = Decimal(str(expense))
    return total_income, total_expense, total_income - total_expense

