from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.crud import log as crud_log
from app.crud import site_content as crud_site_content
from app.models.user import User
from app.schemas.site_content import SiteContentOut, SiteContentUpdate

router = APIRouter()


@router.get("/site-contents", response_model=list[SiteContentOut])
def list_site_contents(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    return crud_site_content.list_all(db)


@router.put("/site-contents/{key}", response_model=SiteContentOut)
def update_site_content(
    key: str,
    data: SiteContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = crud_site_content.get_by_key(db, key)
    if not item:
        raise HTTPException(status_code=404, detail="site content not found")
    item = crud_site_content.update(db, item, data)
    crud_log.add(db, current_user.id, current_user.username, "update", "site_content", item.id, f"update site content {item.key}")
    return item
