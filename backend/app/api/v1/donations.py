from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_roles
from app.crud import donation as crud_donation, log as crud_log
from app.schemas.donation import DonationCreate, DonationUpdate, DonationOut, DonationDetail, PageDonation
from app.models.user import User

router = APIRouter()


def _enrich(d) -> dict:
    """为列表项附加冗余展示字段"""
    out = DonationOut.model_validate(d).model_dump()
    out["donor_name"] = d.donor.name if d.donor else ""
    out["target_name"] = d.target.name if d.target else ""
    return out


@router.get("/donations", response_model=PageDonation)
def list_donations(
    donor_name: str = "",
    target_id: Optional[int] = None,
    status: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    payment_method: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items, total = crud_donation.get_list(
        db, donor_name=donor_name, target_id=target_id, status=status,
        date_from=date_from, date_to=date_to, payment_method=payment_method,
        page=page, page_size=page_size,
    )
    return {"items": [_enrich(d) for d in items], "total": total}


@router.get("/donations/{donation_id}", response_model=DonationDetail)
def get_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    d = crud_donation.get(db, donation_id)
    if not d:
        raise HTTPException(status_code=404, detail="捐款记录不存在")
    logs = crud_log.get_by_target(db, "donation", donation_id)
    result = DonationDetail.model_validate(d).model_dump()
    result["donor_name"] = d.donor.name if d.donor else ""
    result["target_name"] = d.target.name if d.target else ""
    result["logs"] = logs
    return result


@router.post("/donations", response_model=DonationOut, status_code=201)
def create_donation(
    data: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    donation = crud_donation.create(db, data, current_user.id)
    crud_log.add(db, current_user.id, current_user.username, "create", "donation",
                 donation.id, f"新增捐款 {donation.donation_no}")
    out = _enrich(donation)
    return out


@router.put("/donations/{donation_id}", response_model=DonationOut)
def update_donation(
    donation_id: int,
    data: DonationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    donation = crud_donation.get(db, donation_id)
    if not donation:
        raise HTTPException(status_code=404, detail="捐款记录不存在")
    donation = crud_donation.update(db, donation, data)
    crud_log.add(db, current_user.id, current_user.username, "update", "donation",
                 donation_id, f"修改捐款 {donation.donation_no}")
    return _enrich(donation)


@router.delete("/donations/{donation_id}", status_code=204)
def delete_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    donation = crud_donation.get(db, donation_id)
    if not donation:
        raise HTTPException(status_code=404, detail="捐款记录不存在")
    crud_donation.soft_delete(db, donation)
    crud_log.add(db, current_user.id, current_user.username, "delete", "donation",
                 donation_id, f"删除捐款 {donation.donation_no}")
