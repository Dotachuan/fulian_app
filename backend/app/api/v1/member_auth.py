from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.uploads import normalize_public_asset_url
from app.core.config import settings
from app.core.deps import get_current_member, get_db
from app.core.security import create_member_access_token
from app.crud import member as crud_member
from app.schemas.member import (
    MemberAuthLoginIn,
    MemberAuthSendCodeIn,
    MemberAuthSendCodeOut,
    MemberAuthTokenOut,
    MemberAuthWechatPhoneLoginIn,
    MemberPublicOut,
)
from app.services.wechat_miniapp import WechatMiniappError, get_phone_number

router = APIRouter()


def _serialize_member(db: Session, member) -> MemberPublicOut:
    member_level = crud_member.get_member_level(db, member.donor_id)
    return MemberPublicOut(
        id=member.id,
        phone=member.phone,
        name=member.name,
        avatar_url=normalize_public_asset_url(member.avatar_url),
        work_unit=member.work_unit,
        resident_city=member.resident_city,
        donor_id=member.donor_id,
        donor_name=member.donor.name if member.donor else None,
        status=member.status,
        binding_status=member.binding_status,
        binding_source=member.binding_source,
        member_level=member_level,
        member_level_label=crud_member.get_member_level_label(member_level),
        note=member.note,
        first_login_at=member.first_login_at,
        last_login_at=member.last_login_at,
        created_at=member.created_at,
        updated_at=member.updated_at,
    )


@router.post("/member-auth/send-code", response_model=MemberAuthSendCodeOut)
def send_member_login_code(
    data: MemberAuthSendCodeIn,
    db: Session = Depends(get_db),
):
    code = crud_member.create_login_code(db, data.phone)
    return {
        "success": True,
        "phone": data.phone,
        "debug_code": code.code if settings.MEMBER_SMS_DEBUG_RETURN_CODE else None,
        "expires_in_seconds": 300,
    }


@router.post("/member-auth/login", response_model=MemberAuthTokenOut)
def member_login(
    data: MemberAuthLoginIn,
    db: Session = Depends(get_db),
):
    verified = crud_member.verify_login_code(db, data.phone, data.code)
    if not verified:
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    member = crud_member.get_or_create_member_by_phone(db, data.phone)
    member = crud_member.sync_member_binding(db, member)
    member = crud_member.mark_member_login(db, member)
    token = create_member_access_token({"sub": f"member:{member.id}", "token_type": "member"})
    return {"access_token": token, "member": _serialize_member(db, member)}


@router.post("/member-auth/wechat-phone-login", response_model=MemberAuthTokenOut)
def member_wechat_phone_login(
    data: MemberAuthWechatPhoneLoginIn,
    db: Session = Depends(get_db),
):
    try:
        phone_info = get_phone_number(data.phone_code)
    except WechatMiniappError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    member = crud_member.get_or_create_member_by_phone(db, phone_info.pure_phone_number)
    member = crud_member.sync_member_binding(db, member)
    member = crud_member.mark_member_login(db, member)
    token = create_member_access_token({"sub": f"member:{member.id}", "token_type": "member"})
    return {"access_token": token, "member": _serialize_member(db, member)}


@router.get("/member-auth/me", response_model=MemberPublicOut)
def member_me(
    db: Session = Depends(get_db),
    current_member=Depends(get_current_member),
):
    current_member = crud_member.sync_member_binding(db, current_member)
    return _serialize_member(db, current_member)


@router.post("/member-auth/logout")
def member_logout(_: object = Depends(get_current_member)):
    return {"message": "ok"}
