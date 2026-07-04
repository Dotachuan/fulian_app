import re
import uuid
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.core.config import settings
from app.core.deps import require_roles
from app.models.user import User

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 8 * 1024 * 1024


def _safe_folder(folder: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", (folder or "").strip())
    return cleaned or "misc"


def _public_asset_origin(request: Request) -> str:
    configured_origin = (settings.PUBLIC_ASSET_ORIGIN or "").strip().rstrip("/")
    if configured_origin:
        return configured_origin

    forwarded_proto = (request.headers.get("x-forwarded-proto") or "").split(",")[0].strip()
    forwarded_host = (request.headers.get("x-forwarded-host") or "").split(",")[0].strip()
    if forwarded_proto and forwarded_host:
        return f"{forwarded_proto}://{forwarded_host}"

    host = request.headers.get("host") or request.url.netloc
    scheme = request.url.scheme
    if host == "api.fulian520.com" and scheme == "http":
        scheme = "https"
    return f"{scheme}://{host}"


def normalize_public_asset_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return url

    raw = url.strip()
    if not raw:
        return raw

    origin = (settings.PUBLIC_ASSET_ORIGIN or "").strip().rstrip("/")
    if not origin:
        return raw

    if raw.startswith("/uploads/"):
        return f"{origin}{raw}"

    try:
        parsed = urlsplit(raw)
    except ValueError:
        return raw

    host = (parsed.hostname or "").lower()
    path = parsed.path or ""

    if not path.startswith("/uploads/"):
        return raw

    if host in {"127.0.0.1", "localhost"}:
        return f"{origin}{path}"

    if host == "api.fulian520.com" and parsed.scheme == "http":
        return f"{origin}{path}"

    return raw


@router.post("/uploads/image")
async def upload_image(
    request: Request,
    folder: str = Form("misc"),
    file: UploadFile = File(...),
    _: User = Depends(require_roles("admin", "operator")),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="仅支持 jpg、jpeg、png、gif 图片，建议优先上传 jpg 或 png")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="上传文件不能为空")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过 8MB")

    safe_folder = _safe_folder(folder)
    target_folder = Path(settings.UPLOAD_DIR) / safe_folder
    target_folder.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{suffix}"
    target_path = target_folder / filename
    with open(target_path, "wb") as output:
        output.write(content)

    relative_url = f"/uploads/{safe_folder}/{filename}"
    absolute_url = f"{_public_asset_origin(request)}{relative_url}"

    return {
        "filename": filename,
        "folder": safe_folder,
        "relative_url": relative_url,
        "url": absolute_url,
    }
