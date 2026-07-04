from datetime import date
from typing import Optional
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models.donation import Donation
from app.models.donor import Donor
from app.models.target import Target
from app.schemas.donation import DonationCreate, DonationUpdate


def _next_no(db: Session) -> str:
    from datetime import datetime
    prefix = datetime.now().strftime("DN%Y%m%d")
    count = db.query(Donation).filter(Donation.donation_no.like(f"{prefix}%")).count()
    return f"{prefix}{count + 1:04d}"


def get_list(
    db: Session,
    donor_name: str = "",
    target_id: Optional[int] = None,
    status: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    payment_method: str = "",
    page: int = 1,
    page_size: int = 20,
):
    q = (
        db.query(Donation)
        .join(Donor, Donation.donor_id == Donor.id)
        .join(Target, Donation.target_id == Target.id)
        .filter(Donation.is_deleted == False)
    )
    if donor_name:
        q = q.filter(Donor.name.like(f"%{donor_name}%"))
    if target_id:
        q = q.filter(Donation.target_id == target_id)
    if status:
        q = q.filter(Donation.status == status)
    if date_from:
        q = q.filter(Donation.donation_date >= date_from)
    if date_to:
        q = q.filter(Donation.donation_date <= date_to)
    if payment_method:
        q = q.filter(Donation.payment_method == payment_method)

    total = q.count()
    items = q.order_by(Donation.donation_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get(db: Session, donation_id: int) -> Optional[Donation]:
    return (
        db.query(Donation)
        .options(joinedload(Donation.donor), joinedload(Donation.target))
        .filter_by(id=donation_id, is_deleted=False)
        .first()
    )


def create(db: Session, data: DonationCreate, created_by: int) -> Donation:
    donation = Donation(
        donation_no=_next_no(db),
        created_by=created_by,
        **data.model_dump(),
    )
    db.add(donation)
    db.commit()
    db.refresh(donation)
    return donation


def update(db: Session, donation: Donation, data: DonationUpdate) -> Donation:
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(donation, k, v)
    db.commit()
    db.refresh(donation)
    return donation


def soft_delete(db: Session, donation: Donation):
    donation.is_deleted = True
    db.commit()
