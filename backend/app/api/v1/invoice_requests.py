from datetime import date
from io import BytesIO
from typing import Optional

import openpyxl
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.crud import invoice_request as crud_invoice, log as crud_log
from app.models.user import User
from app.schemas.invoice_request import (
    InvoiceRequestBatchUpdate,
    InvoiceRequestOut,
    InvoiceRequestUpdate,
    PageInvoiceRequest,
)

router = APIRouter()
VALID_STATUSES = {"pending", "processed", "rejected"}


@router.get("/invoice-requests", response_model=PageInvoiceRequest)
def list_invoice_requests(
    donor_name: str = "",
    status: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    items, total = crud_invoice.list_requests(
        db,
        donor_name=donor_name,
        status=status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return {"items": items, "total": total}


@router.put("/invoice-requests/{request_id}", response_model=InvoiceRequestOut)
def update_invoice_request(
    request_id: int,
    data: InvoiceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    if data.status and data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="invalid invoice request status")
    request = crud_invoice.get_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="invoice request not found")
    request = crud_invoice.update_request(db, request, data)
    crud_log.add(
        db,
        current_user.id,
        current_user.username,
        "update",
        "invoice_request",
        request.id,
        f"update invoice request {request.request_no}",
    )
    return request


@router.post("/invoice-requests/batch", response_model=list[InvoiceRequestOut])
def batch_update_invoice_requests(
    data: InvoiceRequestBatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    request_ids = list(dict.fromkeys(data.ids))
    if not request_ids:
        raise HTTPException(status_code=400, detail="ids is required")
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="invalid invoice request status")

    updated = crud_invoice.batch_update_requests(
        db,
        request_ids,
        InvoiceRequestUpdate(status=data.status, remark=data.remark),
    )
    if len(updated) != len(request_ids):
        raise HTTPException(status_code=404, detail="some invoice requests not found")

    crud_log.add(
        db,
        current_user.id,
        current_user.username,
        "batch_update",
        "invoice_request",
        None,
        f"batch update invoice requests: {len(updated)}",
    )
    return updated


@router.get("/invoice-requests/export")
def export_invoice_requests(
    donor_name: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    items, _ = crud_invoice.list_requests(
        db,
        donor_name=donor_name,
        status="pending",
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=10000,
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Invoice Requests"
    ws.append([
        "Request No",
        "Donor Name",
        "Amount",
        "Donation Date",
        "Email",
        "Phone",
        "Identity No",
        "Remark",
        "Status",
        "Created At",
        "Processed At",
    ])
    for item in items:
        ws.append([
            item.request_no,
            item.donor_name,
            float(item.amount),
            str(item.donation_date),
            item.email,
            item.phone,
            item.identity_no,
            item.remark or "",
            item.status,
            str(item.created_at),
            str(item.processed_at) if item.processed_at else "",
        ])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=invoice_requests.xlsx"},
    )
