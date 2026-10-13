from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request as UrlRequest, urlopen
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.uploads import normalize_public_asset_url
from app.core.config import settings
from app.core.deps import get_current_member, get_db
from app.crud import fund as crud_fund
from app.crud import invoice_request as crud_invoice
from app.crud import member as crud_member
from app.models.donation import Donation
from app.services.certificate_generator import generate_certificate_image
from app.models.member_suggestion import MemberSuggestion
from app.schemas.fund import FundPublicOut, PublicFundUsagePage
from app.schemas.invoice_request import InvoiceRequestCreate, InvoiceRequestPublicOut
from app.schemas.member import (
    MemberBindingCodeRedeemIn,
    MemberBindingRequestCreate,
    MemberBindingRequestOut,
    MemberAutoBindingIn,
    MemberAutoBindingOut,
    MemberCertificateOut,
    MemberAvatarFromUrlIn,
    MemberDirectoryItem,
    MemberDonationSummary,
    MemberInvoiceProfileOut,
    MemberInvoiceProfileUpdate,
    MemberInvoiceRequestCreate,
    MemberProfileOut,
    MemberProfileUpdate,
    MemberSuggestionCreate,
    MemberSuggestionOut,
    PageMemberDirectory,
    PageMemberDonation,
)

router = APIRouter()

ALLOWED_AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_AVATAR_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}
MAX_AVATAR_SIZE = 5 * 1024 * 1024


def _require_bound_member(member):
    if not member.donor_id:
        raise HTTPException(status_code=409, detail="member donor binding pending")
    return member


def _humanize_fund_description(name: str, description: Optional[str]) -> str:
    if not description:
        return ""
    if "Imported fund mapped from donation target" in description:
        return ""
    return description


def _serialize_member_profile(member) -> MemberProfileOut:
    return {
        "name": member.name or "",
        "avatar_url": normalize_public_asset_url(member.avatar_url) or "",
        "work_unit": member.work_unit or "",
        "resident_city": member.resident_city or "",
        "phone": member.phone or "",
        "phone_note": "电话号码仅用于身份验证，不会在通讯录中公开展示。",
    }


def _serialize_binding_request(item) -> MemberBindingRequestOut:
    return MemberBindingRequestOut(
        id=item.id,
        member_id=item.member_id,
        member_name=item.member.name if item.member else None,
        member_phone=item.member.phone if item.member else None,
        name=item.name,
        phone=item.phone,
        status=item.status,
        donor_id=item.donor_id,
        donor_name=item.donor.name if item.donor else None,
        admin_note=item.admin_note,
        handled_at=item.handled_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _detect_avatar_suffix(filename: str = "", content_type: str = "") -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix in ALLOWED_AVATAR_EXTENSIONS:
        return suffix
    mapped = ALLOWED_AVATAR_CONTENT_TYPES.get((content_type or "").split(";")[0].strip().lower())
    if mapped:
        return mapped
    return ".jpg"


def _save_member_avatar(member_id: int, content: bytes, suffix: str) -> str:
    if not content:
        raise HTTPException(status_code=400, detail="头像文件不能为空")
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="头像大小不能超过 5MB")
    if suffix not in ALLOWED_AVATAR_EXTENSIONS:
        raise HTTPException(status_code=400, detail="仅支持 jpg、jpeg、png、gif、webp 图片")

    target_folder = Path(settings.UPLOAD_DIR) / "member-avatar"
    target_folder.mkdir(parents=True, exist_ok=True)
    filename = f"member_{member_id}_{uuid.uuid4().hex}{suffix}"
    target_path = target_folder / filename
    with open(target_path, "wb") as output:
        output.write(content)
    return f"/uploads/member-avatar/{filename}"


def _download_avatar_from_url(url: str) -> tuple[bytes, str]:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="头像地址仅支持 http 或 https")

    req = UrlRequest(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 FuliianMiniapp/1.0",
            "Accept": "image/*,*/*;q=0.8",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=settings.WECHAT_API_TIMEOUT_SECONDS) as response:
            content_type = response.headers.get("Content-Type", "")
            content = response.read(MAX_AVATAR_SIZE + 1)
    except HTTPError as exc:
        raise HTTPException(status_code=400, detail=f"头像下载失败：HTTP {exc.code}") from exc
    except URLError as exc:
        raise HTTPException(status_code=400, detail=f"头像下载失败：{exc.reason}") from exc

    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="头像大小不能超过 5MB")

    suffix = _detect_avatar_suffix(parsed.path, content_type)
    return content, suffix


@router.post("/member/suggestions", response_model=MemberSuggestionOut, status_code=201)
def create_member_suggestion(
    data: MemberSuggestionCreate,
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    record = MemberSuggestion(
        member_id=current_member.id,
        member_name=current_member.name or "",
        member_phone=current_member.phone or "",
        contact=data.contact or current_member.phone or "",
        content=data.content,
        status="pending",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/member/profile", response_model=MemberProfileOut)
def get_member_profile(current_member=Depends(get_current_member)):
    return _serialize_member_profile(current_member)


@router.put("/member/profile", response_model=MemberProfileOut)
def update_member_profile(
    data: MemberProfileUpdate,
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    member = crud_member.update_member_profile(db, current_member, data)
    return _serialize_member_profile(member)


@router.get("/member/binding-request/latest", response_model=MemberBindingRequestOut | None)
def get_latest_binding_request(
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    item = crud_member.get_latest_member_binding_request(db, current_member.id)
    if not item:
        return None
    return _serialize_binding_request(item)


@router.post("/member/auto-binding", response_model=MemberAutoBindingOut)
def auto_bind_member(
    data: MemberAutoBindingIn,
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    try:
        return crud_member.auto_bind_member_by_name(
            db,
            current_member,
            data.name,
            data.phone,
            confirm_create=data.confirm_create,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/member/binding-correction", response_model=MemberBindingRequestOut, status_code=201)
def create_binding_correction(
    data: MemberBindingRequestCreate,
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    if not current_member.donor_id:
        raise HTTPException(status_code=400, detail="当前账号尚未绑定，请先使用自动匹配")
    if data.phone != current_member.phone:
        raise HTTPException(status_code=400, detail="更正手机号必须与当前登录手机号一致")

    item = crud_member.create_member_binding_request(db, current_member, data.name, data.phone)
    item.admin_note = "用户反馈当前绑定信息有误，请核对后重新绑定。"
    db.commit()
    db.refresh(item)
    return _serialize_binding_request(item)


@router.post("/member/binding-request", response_model=MemberBindingRequestOut, status_code=201)
def create_binding_request(
    data: MemberBindingRequestCreate,
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    if current_member.donor_id:
        raise HTTPException(status_code=400, detail="当前会员已完成绑定")
    item = crud_member.create_member_binding_request(db, current_member, data.name, data.phone)
    current_member.name = data.name
    current_member.binding_status = "unbound"
    db.commit()
    db.refresh(item)
    return _serialize_binding_request(item)


@router.post("/member/profile/avatar", response_model=MemberProfileOut)
async def upload_member_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    suffix = _detect_avatar_suffix(file.filename or "", file.content_type or "")
    content = await file.read()
    current_member.avatar_url = _save_member_avatar(current_member.id, content, suffix)
    db.commit()
    db.refresh(current_member)
    return _serialize_member_profile(current_member)


@router.post("/member/profile/avatar-from-url", response_model=MemberProfileOut)
def sync_member_avatar_from_url(
    data: MemberAvatarFromUrlIn,
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    content, suffix = _download_avatar_from_url(data.avatar_url)
    current_member.avatar_url = _save_member_avatar(current_member.id, content, suffix)
    db.commit()
    db.refresh(current_member)
    return _serialize_member_profile(current_member)


@router.post("/member/binding-code/redeem")
def redeem_member_binding_code(
    data: MemberBindingCodeRedeemIn,
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    try:
        member = crud_member.redeem_binding_code(db, current_member, data.code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "message": "ok",
        "binding_status": member.binding_status,
        "binding_source": member.binding_source,
        "donor_id": member.donor_id,
        "donor_name": member.donor.name if member.donor else None,
    }


@router.get("/member/donations", response_model=PageMemberDonation)
def member_donations(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    year: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    current_member = _require_bound_member(current_member)
    q = db.query(Donation).filter(
        Donation.is_deleted == False,
        Donation.status == "normal",
        Donation.donor_id == current_member.donor_id,
    )
    if year:
        q = q.filter(Donation.donation_date >= date(year, 1, 1), Donation.donation_date <= date(year, 12, 31))
    if date_from:
        q = q.filter(Donation.donation_date >= date_from)
    if date_to:
        q = q.filter(Donation.donation_date <= date_to)
    total = q.count()
    items = q.order_by(Donation.donation_date.desc(), Donation.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [
            {
                "donation_no": item.donation_no,
                "donation_date": item.donation_date,
                "amount": item.amount,
                "target_name": item.target.name if item.target else "",
            }
            for item in items
        ],
        "total": total,
    }


@router.get("/member/donations/summary", response_model=MemberDonationSummary)
def member_donations_summary(
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    current_member = _require_bound_member(current_member)
    total_count, total_amount, first_donation_date = (
        db.query(
            func.count(Donation.id),
            func.coalesce(func.sum(Donation.amount), 0),
            func.min(Donation.donation_date),
        )
        .filter(
            Donation.is_deleted == False,
            Donation.status == "normal",
            Donation.donor_id == current_member.donor_id,
        )
        .one()
    )
    current_year = date.today().year
    first_year = first_donation_date.year if first_donation_date else None
    donor_name = current_member.name or (current_member.donor.name if current_member.donor else current_member.phone)
    return {
        "donor_name": donor_name,
        "total_count": total_count,
        "total_amount": Decimal(str(total_amount)),
        "first_year": first_year,
        "current_year": current_year,
        "support_years": current_year - first_year + 1 if first_year else 0,
    }


@router.get("/member/donations/certificate", response_model=MemberCertificateOut)
def member_certificate(
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    summary = member_donations_summary(db=db, current_member=current_member)
    current_year = date.today().year
    current_year_amount = (
        db.query(func.coalesce(func.sum(Donation.amount), 0))
        .filter(
            Donation.is_deleted == False,
            Donation.status == "normal",
            Donation.donor_id == current_member.donor_id,
            Donation.donation_date >= date(current_year, 1, 1),
            Donation.donation_date <= date(current_year, 12, 31),
        )
        .scalar()
    )
    current_year_amount_decimal = Decimal(str(current_year_amount or 0))
    member_level = crud_member.get_member_level(db, current_member.donor_id)
    issued_on = date.today()
    template_key, poster_url = generate_certificate_image(
        donor_name=summary["donor_name"],
        total_amount=summary["total_amount"],
        current_year_amount=current_year_amount_decimal,
        support_years=summary["support_years"],
        issued_on=issued_on,
        member_level=member_level,
    )
    return {
        **summary,
        "current_year_amount": current_year_amount_decimal,
        "member_level": member_level,
        "member_level_label": crud_member.get_member_level_label(member_level),
        "title": "福莲教育促进会捐赠证书",
        "subtitle": "谨以此证，感谢您对教育公益事业的持续支持。",
        "message": (
            f"感谢您今年捐赠人民币 {current_year_amount_decimal} 元，"
            f"截至目前，您已累计捐赠 {summary['total_amount']} 元。"
        ),
        "footer": "福莲教育促进会",
        "issued_on": issued_on.isoformat(),
        "template_key": template_key,
        "poster_url": poster_url,
    }


@router.get("/member/invoice-profile", response_model=MemberInvoiceProfileOut)
def get_member_invoice_profile(current_member=Depends(get_current_member)):
    return {
        "title": current_member.default_invoice_title or current_member.name or "",
        "phone": current_member.default_invoice_phone or current_member.phone or "",
        "email": current_member.default_invoice_email or "",
        "identity_no": current_member.default_invoice_identity_no or "",
        "remark": current_member.default_invoice_remark or "",
    }


@router.put("/member/invoice-profile", response_model=MemberInvoiceProfileOut)
def update_member_invoice_profile(
    data: MemberInvoiceProfileUpdate,
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    current_member.default_invoice_title = data.title
    current_member.default_invoice_phone = data.phone
    current_member.default_invoice_email = data.email
    current_member.default_invoice_identity_no = data.identity_no
    current_member.default_invoice_remark = data.remark
    db.commit()
    db.refresh(current_member)
    return {
        "title": current_member.default_invoice_title,
        "phone": current_member.default_invoice_phone,
        "email": current_member.default_invoice_email,
        "identity_no": current_member.default_invoice_identity_no,
        "remark": current_member.default_invoice_remark,
    }


@router.post("/member/invoice-requests", response_model=InvoiceRequestPublicOut, status_code=201)
def create_member_invoice_request(
    data: MemberInvoiceRequestCreate,
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    payload = {
        "donor_name": data.donor_name or current_member.default_invoice_title or current_member.name or current_member.phone,
        "amount": data.amount,
        "donation_date": data.donation_date,
        "email": data.email or current_member.default_invoice_email or "",
        "phone": data.phone or current_member.default_invoice_phone or current_member.phone,
        "identity_no": data.identity_no or current_member.default_invoice_identity_no or "",
        "remark": data.remark if data.remark is not None else current_member.default_invoice_remark,
    }
    if not payload["email"] or not payload["identity_no"]:
        raise HTTPException(status_code=400, detail="invoice profile incomplete")

    request = crud_invoice.create_request(db, InvoiceRequestCreate(**payload))
    return request


@router.get("/member/directory", response_model=PageMemberDirectory)
def member_directory(
    name: str = "",
    resident_city: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_member),
):
    items, total = crud_member.list_directory(
        db,
        name=name,
        resident_city=resident_city,
        page=page,
        page_size=page_size,
    )
    level_map = crud_member.get_member_level_map(db, [item.donor_id for item in items if item.donor_id])
    return {
        "items": [
            MemberDirectoryItem(
                id=item.id,
                name=item.name,
                avatar_url=normalize_public_asset_url(item.avatar_url),
                work_unit=item.work_unit,
                resident_city=item.resident_city,
                member_level=level_map.get(item.donor_id, "non_member"),
                member_level_label=crud_member.get_member_level_label(level_map.get(item.donor_id, "non_member")),
            )
            for item in items
        ],
        "total": total,
    }


@router.get("/member/funds")
def member_funds(
    db: Session = Depends(get_db),
    _: object = Depends(get_current_member),
):
    funds, _ = crud_fund.list_funds(db, status="active", page=1, page_size=1000)
    items = []
    for fund in funds:
        total_income, total_expense, balance = crud_fund.fund_totals(db, fund.id)
        items.append(
            FundPublicOut(
                id=fund.id,
                name=fund.name,
                type=fund.type,
                description=_humanize_fund_description(fund.name, fund.description),
                balance=balance,
            )
        )
    return {"items": items}


@router.get("/member/funds/{fund_id}/usage", response_model=PublicFundUsagePage)
def member_fund_usage(
    fund_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_member),
):
    fund = crud_fund.get_fund(db, fund_id)
    if not fund or fund.status != "active":
        raise HTTPException(status_code=404, detail="fund not found")
    records, total = crud_fund.list_usage_records(db, fund_id=fund_id, date_from=date_from, date_to=date_to, page=page, page_size=page_size)
    total_income, total_expense, balance = crud_fund.fund_totals(db, fund_id)
    return {
        "summary": {
            "fund_id": fund.id,
            "fund_name": fund.name,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "description": _humanize_fund_description(fund.name, fund.description),
        },
        "items": [
            {
                "record_date": record.record_date,
                "project_desc": record.project_desc,
                "income_amount": record.income_amount,
                "expense_amount": record.expense_amount,
            }
            for record in records
        ],
        "total": total,
    }
