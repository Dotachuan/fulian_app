from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.uploads import normalize_public_asset_url
from app.core.deps import get_db, require_roles
from app.crud import news as crud_news, log as crud_log
from app.models.user import User
from app.schemas.news import NewsPostCreate, NewsPostOut, NewsPostUpdate, PageNewsPost

router = APIRouter()


def _serialize_news_item(item) -> NewsPostOut:
    return NewsPostOut(
        id=item.id,
        title=item.title,
        summary=item.summary,
        cover_url=normalize_public_asset_url(item.cover_url),
        source_url=item.source_url,
        source=item.source,
        published_at=item.published_at,
        status=item.status,
        is_featured=item.is_featured,
        sort_order=item.sort_order,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/news", response_model=PageNewsPost)
def list_news(
    title: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    items, total = crud_news.get_list(db, title=title, status=status, page=page, page_size=page_size)
    return {"items": [_serialize_news_item(item) for item in items], "total": total}


@router.post("/news", response_model=NewsPostOut, status_code=201)
def create_news(
    data: NewsPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = crud_news.create(db, data)
    crud_log.add(db, current_user.id, current_user.username, "create", "news", item.id, f"create news {item.title}")
    return _serialize_news_item(item)


@router.put("/news/{news_id}", response_model=NewsPostOut)
def update_news(
    news_id: int,
    data: NewsPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = crud_news.get(db, news_id)
    if not item:
        raise HTTPException(status_code=404, detail="news not found")
    item = crud_news.update(db, item, data)
    crud_log.add(db, current_user.id, current_user.username, "update", "news", item.id, f"update news {item.title}")
    return _serialize_news_item(item)


@router.delete("/news/{news_id}", status_code=204)
def delete_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    item = crud_news.get(db, news_id)
    if not item:
        raise HTTPException(status_code=404, detail="news not found")
    crud_news.delete(db, item)
    crud_log.add(db, current_user.id, current_user.username, "delete", "news", news_id, f"delete news {item.title}")
