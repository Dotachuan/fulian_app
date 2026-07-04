from datetime import date
from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.models.donation import Donation
from app.models.donor import Donor
from app.models.target import Target

router = APIRouter()


@router.get("/stats/overview")
def overview(
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    from datetime import datetime
    total_amount = db.query(func.sum(Donation.amount)).filter(Donation.is_deleted == False).scalar() or Decimal("0")
    total_count = db.query(func.count(Donation.id)).filter(Donation.is_deleted == False).scalar() or 0
    donor_count = db.query(func.count(Donor.id)).filter(Donor.is_deleted == False).scalar() or 0

    now = datetime.now()
    month_amount = (
        db.query(func.sum(Donation.amount))
        .filter(
            Donation.is_deleted == False,
            func.year(Donation.donation_date) == now.year,
            func.month(Donation.donation_date) == now.month,
        )
        .scalar()
        or Decimal("0")
    )
    return {
        "total_amount": float(total_amount),
        "total_count": total_count,
        "donor_count": donor_count,
        "month_amount": float(month_amount),
    }


@router.get("/stats/trend")
def trend(
    period: str = "month",
    limit: int = 12,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    q = db.query(Donation).filter(Donation.is_deleted == False)
    if date_from:
        q = q.filter(Donation.donation_date >= date_from)
    if date_to:
        q = q.filter(Donation.donation_date <= date_to)

    if period == "year":
        rows = (
            q.with_entities(
                func.year(Donation.donation_date).label("p"),
                func.sum(Donation.amount).label("amount"),
                func.count(Donation.id).label("count"),
            )
            .group_by("p")
            .order_by("p")
            .limit(limit)
            .all()
        )
        return [{"period": str(r.p), "amount": float(r.amount), "count": r.count} for r in rows]

    if period == "day":
        rows = (
            q.with_entities(
                Donation.donation_date.label("p"),
                func.sum(Donation.amount).label("amount"),
                func.count(Donation.id).label("count"),
            )
            .group_by("p")
            .order_by("p")
            .limit(limit)
            .all()
        )
        return [{"period": str(r.p), "amount": float(r.amount), "count": r.count} for r in rows]

    # default: month
    rows = (
        q.with_entities(
            func.date_format(Donation.donation_date, "%Y-%m").label("p"),
            func.sum(Donation.amount).label("amount"),
            func.count(Donation.id).label("count"),
        )
        .group_by("p")
        .order_by("p")
        .limit(limit)
        .all()
    )
    return [{"period": r.p, "amount": float(r.amount), "count": r.count} for r in rows]


@router.get("/stats/by-target")
def by_target(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    q = (
        db.query(
            Target.name.label("target_name"),
            func.sum(Donation.amount).label("amount"),
        )
        .join(Donation, Donation.target_id == Target.id)
        .filter(Donation.is_deleted == False)
    )
    if date_from:
        q = q.filter(Donation.donation_date >= date_from)
    if date_to:
        q = q.filter(Donation.donation_date <= date_to)
    rows = q.group_by(Target.name).all()
    return [{"target_name": r.target_name, "amount": float(r.amount)} for r in rows]


@router.get("/stats/by-method")
def by_method(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    q = (
        db.query(
            Donation.payment_method.label("method"),
            func.sum(Donation.amount).label("amount"),
        )
        .filter(Donation.is_deleted == False)
    )
    if date_from:
        q = q.filter(Donation.donation_date >= date_from)
    if date_to:
        q = q.filter(Donation.donation_date <= date_to)
    rows = q.group_by(Donation.payment_method).all()
    return [{"method": r.method, "amount": float(r.amount)} for r in rows]
