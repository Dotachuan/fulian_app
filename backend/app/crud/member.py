from datetime import date, datetime, timedelta
from decimal import Decimal
import random
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud import donor as crud_donor
from app.models.donation import Donation
from app.models.donor import Donor
from app.models.member import Member, MemberLoginCode
from app.schemas.member import MemberBindingCodeCreateIn, MemberProfileUpdate, MemberUpdate

MEMBER_LEVEL_DIRECTOR = "director"
MEMBER_LEVEL_MEMBER = "member"
MEMBER_LEVEL_NON_MEMBER = "non_member"
DIRECTOR_DONATION_THRESHOLD = Decimal("30000")

BINDING_SOURCE_AUTO = "auto"
BINDING_SOURCE_MANUAL = "manual"
BINDING_SOURCE_CODE = "code"


def get_member_level_label(level: str) -> str:
    return {
        MEMBER_LEVEL_DIRECTOR: "理事",
        MEMBER_LEVEL_MEMBER: "会员",
        MEMBER_LEVEL_NON_MEMBER: "非会员",
    }.get(level, "非会员")


def _binding_status_for_matches(match_count: int) -> str:
    if match_count == 1:
        return "bound"
    if match_count > 1:
        return "ambiguous"
    return "unbound"


def _is_manual_binding_source(source: Optional[str]) -> bool:
    return source in {BINDING_SOURCE_MANUAL, BINDING_SOURCE_CODE}


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

    matches = find_donor_matches(db, member.phone)
    available_matches = [donor for donor in matches if not donor.binding_bound_member_id or donor.binding_bound_member_id == member.id]

    if len(available_matches) == 1:
        donor = available_matches[0]
        _bind_member_to_donor(db, member, donor, BINDING_SOURCE_AUTO, allow_takeover=False)
    elif len(matches) > 1:
        _release_member_donor(db, member)
        member.binding_status = "ambiguous"
        member.binding_source = BINDING_SOURCE_AUTO
    else:
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
    _ = today
    if not donor_id:
        return MEMBER_LEVEL_NON_MEMBER

    standard_filters = (
        Donation.is_deleted == False,
        Donation.status == "normal",
        Donation.donor_id == donor_id,
    )
    total_count, total_amount = (
        db.query(
            func.count(Donation.id),
            func.coalesce(func.sum(Donation.amount), 0),
        )
        .filter(*standard_filters)
        .one()
    )
    total_count = int(total_count or 0)
    total_amount = Decimal(str(total_amount or 0))

    if total_amount >= DIRECTOR_DONATION_THRESHOLD:
        return MEMBER_LEVEL_DIRECTOR
    if total_count > 0:
        return MEMBER_LEVEL_MEMBER
    return MEMBER_LEVEL_NON_MEMBER


def get_member_level_map(db: Session, donor_ids: list[int], today: Optional[date] = None) -> dict[int, str]:
    _ = today
    donor_ids = [donor_id for donor_id in donor_ids if donor_id]
    if not donor_ids:
        return {}

    standard_filters = (
        Donation.is_deleted == False,
        Donation.status == "normal",
        Donation.donor_id.in_(donor_ids),
    )
    total_rows = (
        db.query(
            Donation.donor_id,
            func.count(Donation.id),
            func.coalesce(func.sum(Donation.amount), 0),
        )
        .filter(*standard_filters)
        .group_by(Donation.donor_id)
        .all()
    )
    total_map = {
        donor_id: {
            "count": int(count or 0),
            "amount": Decimal(str(amount or 0)),
        }
        for donor_id, count, amount in total_rows
    }

    result: dict[int, str] = {}
    for donor_id in donor_ids:
        donor_total = total_map.get(donor_id, {"count": 0, "amount": Decimal("0")})
        if donor_total["amount"] >= DIRECTOR_DONATION_THRESHOLD:
            result[donor_id] = MEMBER_LEVEL_DIRECTOR
        elif donor_total["count"] > 0:
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
    sync_member_binding(db, member)
    db.refresh(member)
    return member


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
