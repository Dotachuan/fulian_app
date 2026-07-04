from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.crud import fund as crud_fund, log as crud_log
from app.models.user import User
from app.schemas.fund import (
    FundCreate,
    FundOut,
    FundUpdate,
    FundUsageCreate,
    FundUsageOut,
    FundUsageUpdate,
    PageFund,
    PageFundUsage,
)

router = APIRouter()


@router.get("/funds", response_model=PageFund)
def list_funds(
    status: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    items, total = crud_fund.list_funds(db, status=status, page=page, page_size=page_size)
    return {"items": items, "total": total}


@router.post("/funds", response_model=FundOut, status_code=201)
def create_fund(
    data: FundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    fund = crud_fund.create_fund(db, data)
    crud_log.add(db, current_user.id, current_user.username, "create", "fund", fund.id, f"create fund {fund.name}")
    return fund


@router.put("/funds/{fund_id}", response_model=FundOut)
def update_fund(
    fund_id: int,
    data: FundUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    fund = crud_fund.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(status_code=404, detail="fund not found")
    fund = crud_fund.update_fund(db, fund, data)
    crud_log.add(db, current_user.id, current_user.username, "update", "fund", fund.id, f"update fund {fund.name}")
    return fund


@router.delete("/funds/{fund_id}", status_code=204)
def delete_fund(
    fund_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    fund = crud_fund.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(status_code=404, detail="fund not found")
    crud_fund.delete_fund(db, fund)
    crud_log.add(db, current_user.id, current_user.username, "delete", "fund", fund_id, f"delete fund {fund.name}")


@router.get("/fund-usage-records", response_model=PageFundUsage)
def list_usage_records(
    fund_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    items, total = crud_fund.list_usage_records(
        db,
        fund_id=fund_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return {"items": items, "total": total}


@router.post("/fund-usage-records", response_model=FundUsageOut, status_code=201)
def create_usage_record(
    data: FundUsageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    if not crud_fund.get_fund(db, data.fund_id):
        raise HTTPException(status_code=404, detail="fund not found")
    record = crud_fund.create_usage_record(db, data)
    crud_log.add(
        db,
        current_user.id,
        current_user.username,
        "create",
        "fund_usage",
        record.id,
        f"create fund usage {record.project_desc}",
    )
    return record


@router.put("/fund-usage-records/{record_id}", response_model=FundUsageOut)
def update_usage_record(
    record_id: int,
    data: FundUsageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    record = crud_fund.get_usage_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="usage record not found")
    record = crud_fund.update_usage_record(db, record, data)
    crud_log.add(
        db,
        current_user.id,
        current_user.username,
        "update",
        "fund_usage",
        record.id,
        f"update fund usage {record.project_desc}",
    )
    return record


@router.delete("/fund-usage-records/{record_id}", status_code=204)
def delete_usage_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    record = crud_fund.get_usage_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="usage record not found")
    crud_fund.delete_usage_record(db, record)
    crud_log.add(db, current_user.id, current_user.username, "delete", "fund_usage", record_id, "delete fund usage")

