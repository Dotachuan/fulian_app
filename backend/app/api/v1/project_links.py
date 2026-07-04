from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.uploads import normalize_public_asset_url
from app.core.deps import get_db, require_roles
from app.crud import log as crud_log
from app.crud import project_link as crud_project_link
from app.models.user import User
from app.schemas.project_link import PageProjectLink, ProjectLinkCreate, ProjectLinkOut, ProjectLinkUpdate

router = APIRouter()


def _serialize_project_link(item) -> ProjectLinkOut:
    return ProjectLinkOut(
        id=item.id,
        section_key=item.section_key,
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


@router.get("/project-links", response_model=PageProjectLink)
def list_project_links(
    title: str = "",
    status: str = "",
    section_key: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    items, total = crud_project_link.get_list(
        db,
        title=title,
        status=status,
        section_key=section_key,
        page=page,
        page_size=page_size,
    )
    return {"items": [_serialize_project_link(item) for item in items], "total": total}


@router.post("/project-links", response_model=ProjectLinkOut, status_code=201)
def create_project_link(
    data: ProjectLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = crud_project_link.create(db, data)
    crud_log.add(db, current_user.id, current_user.username, "create", "project_link", item.id, f"create project link {item.title}")
    return _serialize_project_link(item)


@router.put("/project-links/{item_id}", response_model=ProjectLinkOut)
def update_project_link(
    item_id: int,
    data: ProjectLinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = crud_project_link.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="project link not found")
    item = crud_project_link.update(db, item, data)
    crud_log.add(db, current_user.id, current_user.username, "update", "project_link", item.id, f"update project link {item.title}")
    return _serialize_project_link(item)


@router.delete("/project-links/{item_id}", status_code=204)
def delete_project_link(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    item = crud_project_link.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="project link not found")
    crud_project_link.delete(db, item)
    crud_log.add(db, current_user.id, current_user.username, "delete", "project_link", item_id, f"delete project link {item.title}")
