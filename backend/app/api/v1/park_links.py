from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.uploads import normalize_public_asset_url
from app.core.deps import get_db, require_roles
from app.crud import log as crud_log
from app.crud import park_link as crud_park_link
from app.models.user import User
from app.schemas.park_link import PageParkLink, ParkLinkCreate, ParkLinkOut, ParkLinkUpdate

router = APIRouter()


def _serialize_park_link(item) -> ParkLinkOut:
    return ParkLinkOut(
        id=item.id,
        title=item.title,
        summary=item.summary,
        image_url=normalize_public_asset_url(item.image_url),
        target_url=item.target_url,
        status=item.status,
        is_featured=item.is_featured,
        published_at=item.published_at,
        sort_order=item.sort_order,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/park-links", response_model=PageParkLink)
def list_park_links(
    title: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    items, total = crud_park_link.get_list(db, title=title, status=status, page=page, page_size=page_size)
    return {"items": [_serialize_park_link(item) for item in items], "total": total}


@router.post("/park-links", response_model=ParkLinkOut, status_code=201)
def create_park_link(
    data: ParkLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = crud_park_link.create(db, data)
    crud_log.add(db, current_user.id, current_user.username, "create", "park_link", item.id, f"create park link {item.title}")
    return _serialize_park_link(item)


@router.put("/park-links/{item_id}", response_model=ParkLinkOut)
def update_park_link(
    item_id: int,
    data: ParkLinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = crud_park_link.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="park link not found")
    item = crud_park_link.update(db, item, data)
    crud_log.add(db, current_user.id, current_user.username, "update", "park_link", item.id, f"update park link {item.title}")
    return _serialize_park_link(item)


@router.delete("/park-links/{item_id}", status_code=204)
def delete_park_link(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    item = crud_park_link.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="park link not found")
    crud_park_link.delete(db, item)
    crud_log.add(db, current_user.id, current_user.username, "delete", "park_link", item_id, f"delete park link {item.title}")
