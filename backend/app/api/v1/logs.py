from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.crud import log as crud_log
from app.schemas.log import PageLog

router = APIRouter()


@router.get("/logs", response_model=PageLog)
def list_logs(
    action: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    items, total = crud_log.get_list(
        db, action=action, date_from=date_from, date_to=date_to,
        page=page, page_size=page_size,
    )
    return {"items": items, "total": total}
