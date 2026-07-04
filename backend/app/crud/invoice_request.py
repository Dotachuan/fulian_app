from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.invoice_request import InvoiceRequest
from app.schemas.invoice_request import InvoiceRequestCreate, InvoiceRequestUpdate


def _next_no(db: Session) -> str:
    prefix = datetime.now().strftime("INV%Y%m%d")
    count = db.query(InvoiceRequest).filter(InvoiceRequest.request_no.like(f"{prefix}%")).count()
    return f"{prefix}{count + 1:04d}"


def list_requests(
    db: Session,
    donor_name: str = "",
    status: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(InvoiceRequest)
    if donor_name:
        q = q.filter(InvoiceRequest.donor_name.like(f"%{donor_name}%"))
    if status:
        q = q.filter(InvoiceRequest.status == status)
    if date_from:
        q = q.filter(InvoiceRequest.donation_date >= date_from)
    if date_to:
        q = q.filter(InvoiceRequest.donation_date <= date_to)
    total = q.count()
    items = q.order_by(InvoiceRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_request(db: Session, request_id: int) -> Optional[InvoiceRequest]:
    return db.get(InvoiceRequest, request_id)


def create_request(db: Session, data: InvoiceRequestCreate) -> InvoiceRequest:
    request = InvoiceRequest(request_no=_next_no(db), **data.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def update_request(db: Session, request: InvoiceRequest, data: InvoiceRequestUpdate) -> InvoiceRequest:
    old_status = request.status
    values = data.model_dump(exclude_none=True)
    for key, value in values.items():
        setattr(request, key, value)
    if values.get("status") and values["status"] != old_status and values["status"] != "pending":
        request.processed_at = datetime.now()
    db.commit()
    db.refresh(request)
    return request


def batch_update_requests(
    db: Session,
    request_ids: list[int],
    data: InvoiceRequestUpdate,
) -> list[InvoiceRequest]:
    if not request_ids:
        return []

    items = db.query(InvoiceRequest).filter(InvoiceRequest.id.in_(request_ids)).all()
    if len(items) != len(request_ids):
        return items

    values = data.model_dump(exclude_none=True)
    now = datetime.now()
    for item in items:
        old_status = item.status
        for key, value in values.items():
            setattr(item, key, value)
        if values.get("status") and values["status"] != old_status and values["status"] != "pending":
            item.processed_at = now
    db.commit()
    for item in items:
        db.refresh(item)
    return items
