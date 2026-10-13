from datetime import date, datetime, timedelta
from decimal import Decimal
import random
import re
import unicodedata
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud import donor as crud_donor
from app.models.donation import Donation
from app.models.donor import Donor
from app.models.member import Member, MemberLoginCode
from app.models.member_binding_request import MemberBindingRequest
from app.schemas.member import MemberBindingCodeCreateIn, MemberProfileUpdate, MemberUpdate

MEMBER_LEVEL_DIRECTOR = "director"
MEMBER_LEVEL_MEMBER = "member"
MEMBER_LEVEL_NON_MEMBER = "non_member"
DIRECTOR_TOTAL_DONATION_THRESHOLD = Decimal("200000")
DIRECTOR_RECENT_FIVE_YEAR_THRESHOLD = Decimal("15000")
MEMBER_ANNUAL_DONATION_STANDARD = Decimal("5000")

BINDING_SOURCE_AUTO = "auto"
BINDING_SOURCE_MANUAL = "manual"
BINDING_SOURCE_CODE = "code"
BINDING_SOURCE_REQUEST = "request"


def get_member_level_label(level: str) -> str:
    return {
        MEMBER_LEVEL_DIRECTOR: "理事捐赠人",
        MEMBER_LEVEL_MEMBER: "会员捐赠人",
        MEMBER_LEVEL_NON_MEMBER: "非会员",
    }.get(level, "非会员")

def _binding_status_for_matches(match_count: int) -> str:
    if match_count == 1:
        return "bound"
    if match_count > 1:
        return "ambiguous"
    return "unbound"


def _is_manual_binding_source(source: Optional[str]) -> bool:
    return source in {BINDING_SOURCE_MANUAL, BINDING_SOURCE_CODE, BINDING_SOURCE_REQUEST}


def _release_member_donor(db: Session, member: Member):
    if not member.donor_id:
        return
    donor = db.get(Donor, member.donor_id)
    if donor and donor.binding_bound_member_id == member.id:
        crud_donor.set_binding_member(db, donor, None)
    member.donor_id = None


def _bind_member_to_donor(
    db: Session,
    member: Member,
    donor: Donor,
    source: str,
    *,
    allow_takeover: bool,
):
    if donor.binding_bound_member_id and donor.binding_bound_member_id != member.id:
        if not allow_takeover:
            return False
        previous_member = db.get(Member, donor.binding_bound_member_id)
        if previous_member and previous_member.donor_id == donor.id:
            previous_member.donor_id = None
            previous_member.binding_status = "unbound"
            previous_member.binding_source = BINDING_SOURCE_AUTO

    if member.donor_id and member.donor_id != donor.id:
        _release_member_donor(db, member)

    member.donor_id = donor.id
    member.binding_status = "bound"
    member.binding_source = source
    if not member.name:
        member.name = donor.name
    crud_donor.set_binding_member(db, donor, member.id)
    return True


def find_donor_matches(db: Session, phone: str) -> list[Donor]:
    return (
        db.query(Donor)
        .filter(Donor.is_deleted == False)
        .filter(Donor.phone == phone)
        .order_by(Donor.id.asc())
        .all()
    )


def get_or_create_member_by_phone(db: Session, phone: str) -> Member:
    member = db.query(Member).filter(Member.phone == phone).first()
    if member:
        return member

    member = Member(
        phone=phone,
        binding_status="unbound",
        binding_source=BINDING_SOURCE_AUTO,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return sync_member_binding(db, member)


def sync_member_binding(db: Session, member: Member) -> Member:
    if member.donor_id:
        donor = db.get(Donor, member.donor_id)
        if donor and donor.is_deleted == False:
            if _is_manual_binding_source(member.binding_source):
                _bind_member_to_donor(db, member, donor, member.binding_source, allow_takeover=True)
                db.commit()
                db.refresh(member)
                return member

            if donor.phone == member.phone and _bind_member_to_donor(
                db,
                member,
                donor,
                BINDING_SOURCE_AUTO,
                allow_takeover=False,
            ):
                db.commit()
                db.refresh(member)
                return member

    _release_member_donor(db, member)
    member.binding_status = "unbound"
    member.binding_source = BINDING_SOURCE_AUTO

    db.commit()
    db.refresh(member)
    return member


def create_login_code(db: Session, phone: str, expires_in_seconds: int = 300) -> MemberLoginCode:
    db.query(MemberLoginCode).filter(
        MemberLoginCode.phone == phone,
        MemberLoginCode.status == "pending",
    ).update({"status": "expired"})
    code = f"{random.randint(0, 999999):06d}"
    item = MemberLoginCode(
        phone=phone,
        code=code,
        expires_at=datetime.now() + timedelta(seconds=expires_in_seconds),
        status="pending",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def verify_login_code(db: Session, phone: str, code: str) -> Optional[MemberLoginCode]:
    item = (
        db.query(MemberLoginCode)
        .filter(MemberLoginCode.phone == phone, MemberLoginCode.code == code, MemberLoginCode.status == "pending")
        .order_by(MemberLoginCode.id.desc())
        .first()
    )
    if not item or item.expires_at < datetime.now():
        return None
    item.status = "used"
    item.used_at = datetime.now()
    db.commit()
    db.refresh(item)
    return item


def mark_member_login(db: Session, member: Member) -> Member:
    now = datetime.now()
    if not member.first_login_at:
        member.first_login_at = now
    member.last_login_at = now
    db.commit()
    db.refresh(member)
    return member


def get_member(db: Session, member_id: int) -> Optional[Member]:
    return db.get(Member, member_id)


def get_member_level(db: Session, donor_id: Optional[int], today: Optional[date] = None) -> str:
    today = today or date.today()
    if not donor_id:
        return MEMBER_LEVEL_NON_MEMBER

    donations = (
        db.query(Donation.donation_date, Donation.amount)
        .filter(
            Donation.is_deleted == False,
            Donation.status == "normal",
            Donation.donor_id == donor_id,
        )
        .all()
    )
    if not donations:
        return MEMBER_LEVEL_NON_MEMBER

    recent_start = date(today.year - 4, 1, 1)
    total_amount = Decimal("0")
    recent_five_year_amount = Decimal("0")
    amount_by_year: dict[int, Decimal] = {}

    for donation_date, amount in donations:
        donation_amount = Decimal(str(amount or 0))
        total_amount += donation_amount
        if donation_date and donation_date >= recent_start:
            recent_five_year_amount += donation_amount
        if donation_date:
            amount_by_year[donation_date.year] = amount_by_year.get(donation_date.year, Decimal("0")) + donation_amount

    if (
        total_amount >= DIRECTOR_TOTAL_DONATION_THRESHOLD
        or recent_five_year_amount >= DIRECTOR_RECENT_FIVE_YEAR_THRESHOLD
    ):
        return MEMBER_LEVEL_DIRECTOR
    if any(year_amount >= MEMBER_ANNUAL_DONATION_STANDARD for year_amount in amount_by_year.values()):
        return MEMBER_LEVEL_MEMBER
    return MEMBER_LEVEL_NON_MEMBER


def get_member_level_map(db: Session, donor_ids: list[int], today: Optional[date] = None) -> dict[int, str]:
    today = today or date.today()
    donor_ids = [donor_id for donor_id in donor_ids if donor_id]
    if not donor_ids:
        return {}

    rows = (
        db.query(Donation.donor_id, Donation.donation_date, Donation.amount)
        .filter(
            Donation.is_deleted == False,
            Donation.status == "normal",
            Donation.donor_id.in_(donor_ids),
        )
        .all()
    )
    recent_start = date(today.year - 4, 1, 1)
    total_map: dict[int, dict] = {}

    for donor_id, donation_date, amount in rows:
        donor_total = total_map.setdefault(
            donor_id,
            {
                "amount": Decimal("0"),
                "recent_five_year_amount": Decimal("0"),
                "amount_by_year": {},
            },
        )
        donation_amount = Decimal(str(amount or 0))
        donor_total["amount"] += donation_amount
        if donation_date and donation_date >= recent_start:
            donor_total["recent_five_year_amount"] += donation_amount
        if donation_date:
            donor_total["amount_by_year"][donation_date.year] = (
                donor_total["amount_by_year"].get(donation_date.year, Decimal("0")) + donation_amount
            )

    result: dict[int, str] = {}
    for donor_id in donor_ids:
        donor_total = total_map.get(
            donor_id,
            {
                "amount": Decimal("0"),
                "recent_five_year_amount": Decimal("0"),
                "amount_by_year": {},
            },
        )
        if (
            donor_total["amount"] >= DIRECTOR_TOTAL_DONATION_THRESHOLD
            or donor_total["recent_five_year_amount"] >= DIRECTOR_RECENT_FIVE_YEAR_THRESHOLD
        ):
            result[donor_id] = MEMBER_LEVEL_DIRECTOR
        elif any(year_amount >= MEMBER_ANNUAL_DONATION_STANDARD for year_amount in donor_total["amount_by_year"].values()):
            result[donor_id] = MEMBER_LEVEL_MEMBER
        else:
            result[donor_id] = MEMBER_LEVEL_NON_MEMBER
    return result

def list_members(
    db: Session,
    keyword: str = "",
    status: str = "",
    binding_status: str = "",
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(Member)
    if keyword:
        q = q.filter((Member.phone.like(f"%{keyword}%")) | (Member.name.like(f"%{keyword}%")))
    if status:
        q = q.filter(Member.status == status)
    if binding_status:
        q = q.filter(Member.binding_status == binding_status)
    total = q.count()
    items = q.order_by(Member.created_at.desc(), Member.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total

def update_member(db: Session, member: Member, data: MemberUpdate) -> Member:
    values = data.model_dump(exclude_unset=True)
    sync_donor_phone = values.pop("sync_donor_phone", False)
    donor_id_set = "donor_id" in values

    for key, value in values.items():
        setattr(member, key, value)

    if donor_id_set:
        if member.donor_id:
            donor = db.get(Donor, member.donor_id)
            if donor and donor.is_deleted == False:
                _bind_member_to_donor(db, member, donor, BINDING_SOURCE_MANUAL, allow_takeover=True)
                if sync_donor_phone:
                    donor.phone = member.phone
        else:
            _release_member_donor(db, member)
            member.binding_status = "unbound"
            member.binding_source = BINDING_SOURCE_AUTO
    else:
        sync_member_binding(db, member)
        member = db.get(Member, member.id)
        if sync_donor_phone and member.donor_id:
            donor = db.get(Donor, member.donor_id)
            if donor and donor.is_deleted == False:
                donor.phone = member.phone

    db.commit()
    db.refresh(member)
    return member


def update_member_profile(db: Session, member: Member, data: MemberProfileUpdate) -> Member:
    member.name = data.name
    member.work_unit = data.work_unit or None
    member.resident_city = data.resident_city or None
    member.phone = data.phone
    if not member.donor_id:
        member.binding_status = "unbound"
        member.binding_source = BINDING_SOURCE_AUTO
    db.commit()
    db.refresh(member)
    return member


def create_member_binding_request(db: Session, member: Member, name: str, phone: str) -> MemberBindingRequest:
    pending = (
        db.query(MemberBindingRequest)
        .filter(
            MemberBindingRequest.member_id == member.id,
            MemberBindingRequest.status == "pending",
        )
        .order_by(MemberBindingRequest.id.desc())
        .first()
    )
    if pending:
        pending.name = name
        pending.phone = phone
        db.commit()
        db.refresh(pending)
        return pending

    item = MemberBindingRequest(
        member_id=member.id,
        name=name,
        phone=phone,
        status="pending",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _normalize_binding_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"\s+", "", normalized).strip()


def _normalize_binding_phone(value: Optional[str]) -> str:
    digits = re.sub(r"\D+", "", value or "")
    if len(digits) == 13 and digits.startswith("86"):
        return digits[2:]
    return digits


def _find_donors_by_name(db: Session, name: str) -> list[Donor]:
    normalized_name = _normalize_binding_name(name)
    donors = db.query(Donor).filter(Donor.is_deleted == False).order_by(Donor.id.asc()).all()
    return [donor for donor in donors if _normalize_binding_name(donor.name) == normalized_name]


def _resolve_pending_binding_requests(db: Session, member: Member, donor: Donor, note: str) -> None:
    pending_items = (
        db.query(MemberBindingRequest)
        .filter(
            MemberBindingRequest.member_id == member.id,
            MemberBindingRequest.status == "pending",
        )
        .all()
    )
    for item in pending_items:
        item.status = "approved"
        item.donor_id = donor.id
        item.admin_note = note
        item.handled_at = datetime.now()


def _queue_binding_review(db: Session, member: Member, name: str, phone: str, reason: str) -> dict:
    item = create_member_binding_request(db, member, name, phone)
    item.admin_note = reason
    member.name = name
    member.binding_status = "ambiguous"
    member.binding_source = BINDING_SOURCE_REQUEST
    db.commit()
    db.refresh(item)
    return {
        "result": "manual_review",
        "message": reason,
        "request_id": item.id,
    }


def auto_bind_member_by_name(
    db: Session,
    member: Member,
    name: str,
    phone: str,
    *,
    confirm_create: bool = False,
) -> dict:
    submitted_name = unicodedata.normalize("NFKC", name or "").strip()
    submitted_phone = _normalize_binding_phone(phone)
    member_phone = _normalize_binding_phone(member.phone)

    if submitted_phone != member_phone:
        raise ValueError("绑定手机号必须与当前登录手机号一致")

    if member.donor_id:
        donor = db.get(Donor, member.donor_id)
        if donor and donor.is_deleted == False:
            return {
                "result": "bound",
                "message": "当前账号已完成绑定",
                "donor_id": donor.id,
                "donor_name": donor.name,
            }

    matches = _find_donors_by_name(db, submitted_name)
    if len(matches) > 1:
        return _queue_binding_review(
            db,
            member,
            submitted_name,
            member.phone,
            "检测到多个同名档案，请等待管理员确认。",
        )

    if len(matches) == 1:
        donor = matches[0]
        if donor.binding_bound_member_id and donor.binding_bound_member_id != member.id:
            return _queue_binding_review(
                db,
                member,
                submitted_name,
                member.phone,
                "该姓名档案已绑定其他账号，请等待管理员确认。",
            )

        donor_phone = _normalize_binding_phone(donor.phone)
        if donor_phone and donor_phone != member_phone:
            return _queue_binding_review(
                db,
                member,
                submitted_name,
                member.phone,
                "姓名已匹配，但预留手机号不一致，请等待管理员确认。",
            )

        if not donor.phone:
            donor.phone = member.phone
        member.name = donor.name
        _bind_member_to_donor(db, member, donor, BINDING_SOURCE_AUTO, allow_takeover=False)
        _resolve_pending_binding_requests(db, member, donor, "系统已按姓名自动匹配。")
        db.commit()
        db.refresh(member)
        return {
            "result": "bound",
            "message": "已匹配到会员档案并完成绑定",
            "donor_id": donor.id,
            "donor_name": donor.name,
        }

    if not confirm_create:
        return {
            "result": "confirm_create",
            "message": "未找到对应会员档案，请核对姓名；确认无误后可创建新档案。",
            "donor_name": submitted_name,
        }

    donor = Donor(name=submitted_name, type="person", phone=member.phone)
    db.add(donor)
    db.flush()
    member.name = submitted_name
    _bind_member_to_donor(db, member, donor, BINDING_SOURCE_AUTO, allow_takeover=False)
    _resolve_pending_binding_requests(db, member, donor, "系统已创建新档案并完成绑定。")
    db.commit()
    db.refresh(member)
    return {
        "result": "bound",
        "message": "已创建新档案并完成绑定",
        "donor_id": donor.id,
        "donor_name": donor.name,
    }


def get_latest_member_binding_request(db: Session, member_id: int) -> Optional[MemberBindingRequest]:
    return (
        db.query(MemberBindingRequest)
        .filter(MemberBindingRequest.member_id == member_id)
        .order_by(MemberBindingRequest.id.desc())
        .first()
    )


def list_member_binding_requests(
    db: Session,
    keyword: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(MemberBindingRequest)
    if keyword:
        like = f"%{keyword.strip()}%"
        q = q.join(Member, MemberBindingRequest.member_id == Member.id).filter(
            (MemberBindingRequest.name.like(like))
            | (MemberBindingRequest.phone.like(like))
            | (Member.phone.like(like))
            | (Member.name.like(like))
        )
    if status:
        q = q.filter(MemberBindingRequest.status == status)
    total = q.count()
    items = (
        q.order_by(MemberBindingRequest.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total

def approve_member_binding_request(
    db: Session,
    item: MemberBindingRequest,
    donor_id: int,
    admin_user_id: int,
    admin_note: str = "",
) -> MemberBindingRequest:
    member = db.get(Member, item.member_id)
    donor = db.get(Donor, donor_id)
    if not member:
        raise ValueError("member not found")
    if not donor or donor.is_deleted:
        raise ValueError("donor not found")
    _bind_member_to_donor(db, member, donor, BINDING_SOURCE_REQUEST, allow_takeover=True)
    if not member.name:
        member.name = item.name
    item.status = "approved"
    item.donor_id = donor.id
    item.admin_note = admin_note or None
    item.handled_by = admin_user_id
    item.handled_at = datetime.now()
    db.commit()
    db.refresh(item)
    return item


def reject_member_binding_request(
    db: Session,
    item: MemberBindingRequest,
    admin_user_id: int,
    admin_note: str = "",
) -> MemberBindingRequest:
    item.status = "rejected"
    item.admin_note = admin_note or None
    item.handled_by = admin_user_id
    item.handled_at = datetime.now()
    db.commit()
    db.refresh(item)
    return item


def list_donor_candidates(db: Session, keyword: str = "", page_size: int = 20):
    q = db.query(Donor).filter(Donor.is_deleted == False)
    if keyword:
        q = q.filter((Donor.name.like(f"%{keyword}%")) | (Donor.phone.like(f"%{keyword}%")))
    return q.order_by(Donor.name.asc(), Donor.id.asc()).limit(page_size).all()


def create_binding_code(
    db: Session,
    member: Member,
    data: MemberBindingCodeCreateIn,
) -> Donor:
    donor = db.get(Donor, data.donor_id)
    if not donor or donor.is_deleted:
        raise ValueError("donor not found")
    donor = crud_donor.ensure_binding_code(db, donor)
    if donor.binding_code_status == "disabled":
        donor.binding_code_status = "bound" if donor.binding_bound_member_id else "active"
        db.commit()
        db.refresh(donor)
    return donor


def get_latest_pending_binding_code(db: Session, member_id: int) -> Optional[Donor]:
    member = db.get(Member, member_id)
    if not member or not member.donor_id:
        return None
    donor = db.get(Donor, member.donor_id)
    if donor and donor.binding_code:
        return donor
    return None


def redeem_binding_code(db: Session, member: Member, code_text: str) -> Member:
    donor = crud_donor.get_by_binding_code(db, code_text.strip().upper())
    if not donor or donor.is_deleted:
        raise ValueError("binding code not found")
    if donor.binding_code_status not in {"active", "bound"}:
        raise ValueError("binding code is unavailable")
    if donor.binding_bound_member_id and donor.binding_bound_member_id != member.id:
        raise ValueError("binding code already used")

    _bind_member_to_donor(db, member, donor, BINDING_SOURCE_CODE, allow_takeover=True)
    db.commit()
    db.refresh(member)
    return member


def list_directory(
    db: Session,
    name: str = "",
    resident_city: str = "",
    page: int = 1,
    page_size: int = 20,
):
    q = (
        db.query(Member)
        .filter(Member.status == "active")
        .filter(Member.binding_status == "bound")
        .filter(Member.name.isnot(None))
    )
    if name:
        q = q.filter(Member.name.like(f"%{name.strip()}%"))
    if resident_city:
        q = q.filter(Member.resident_city.like(f"%{resident_city.strip()}%"))
    total = q.count()
    items = (
        q.order_by(Member.name.asc(), Member.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total
