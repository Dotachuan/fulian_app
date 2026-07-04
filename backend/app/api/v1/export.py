from datetime import date
from typing import Optional
from io import BytesIO

import openpyxl
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.crud import donation as crud_donation

router = APIRouter()


@router.get("/donations/export")
def export_donations(
    donor_name: str = "",
    target_id: Optional[int] = None,
    status: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    items, _ = crud_donation.get_list(
        db, donor_name=donor_name, target_id=target_id, status=status,
        date_from=date_from, date_to=date_to, page=1, page_size=10000,
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "捐款记录"

    headers = ["捐款编号", "捐款日期", "捐款人", "金额（元）", "捐款目标", "捐款方式", "是否开票", "票据编号", "状态", "录入时间"]
    ws.append(headers)

    for d in items:
        ws.append([
            d.donation_no,
            str(d.donation_date),
            d.donor.name if d.donor else "",
            float(d.amount),
            d.target.name if d.target else "",
            d.payment_method,
            "是" if d.receipt_flag else "否",
            d.receipt_no or "",
            d.status,
            str(d.created_at),
        ])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=donations.xlsx"},
    )
