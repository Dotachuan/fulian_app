from io import BytesIO

import openpyxl
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.v1.uploads import normalize_public_asset_url
from app.core.deps import get_db, require_roles
from app.crud import log as crud_log
from app.crud import member as crud_member
from app.models.member_suggestion import MemberSuggestion
from app.models.member_binding_request import MemberBindingRequest
from app.models.user import User
from app.schemas.donor import DonorOut
from app.schemas.member import (
    MemberBindingCodeCreateIn,
    MemberBindingCodeOut,
    MemberBindingRequestApproveIn,
    MemberBindingRequestOut,
    MemberBindingRequestRejectIn,
    MemberSuggestionAdminOut,
    MemberSuggestionAdminUpdate,
    MemberPublicOut,
    MemberUpdate,
    PageMemberBindingRequest,
    PageMemberSuggestion,
    PageMember,
)

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


def _serialize_binding_code(item) -> MemberBindingCodeOut:
    return MemberBindingCodeOut(
        id=item.id,
        code=item.binding_code,
        member_id=item.binding_bound_member_id or 0,
        donor_id=item.id,
        donor_name=item.name,
        status=item.binding_code_status or "active",
        note=item.remark,
        expires_at=item.created_at,
        used_at=item.binding_bound_at,
        created_at=item.created_at,
    )


def _serialize_suggestion(item: MemberSuggestion) -> MemberSuggestionAdminOut:
    return MemberSuggestionAdminOut(
        id=item.id,
        member_id=item.member_id,
        member_name=item.member_name or "",
        member_phone=item.member_phone or "",
        contact=item.contact or "",
        content=item.content,
        status=item.status,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _serialize_binding_request(item: MemberBindingRequest) -> MemberBindingRequestOut:
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


@router.get("/members", response_model=PageMember)
def list_members(
    keyword: str = "",
    status: str = "",
    binding_status: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    items, total = crud_member.list_members(
        db,
        keyword=keyword,
        status=status,
        binding_status=binding_status,
        page=page,
        page_size=page_size,
    )
    return {"items": [_serialize_member(db, item) for item in items], "total": total}


@router.get("/members/suggestions", response_model=PageMemberSuggestion)
def list_member_suggestions(
    keyword: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    q = db.query(MemberSuggestion)
    if keyword:
        like = f"%{keyword.strip()}%"
        q = q.filter(
            or_(
                MemberSuggestion.member_name.ilike(like),
                MemberSuggestion.member_phone.ilike(like),
                MemberSuggestion.contact.ilike(like),
                MemberSuggestion.content.ilike(like),
            )
        )
    if status:
        q = q.filter(MemberSuggestion.status == status)

    total = q.count()
    items = (
        q.order_by(MemberSuggestion.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"items": [_serialize_suggestion(item) for item in items], "total": total}


@router.put("/members/suggestions/{suggestion_id}", response_model=MemberSuggestionAdminOut)
def update_member_suggestion(
    suggestion_id: int,
    data: MemberSuggestionAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = db.get(MemberSuggestion, suggestion_id)
    if not item:
        raise HTTPException(status_code=404, detail="suggestion not found")
    item.status = data.status
    db.commit()
    db.refresh(item)
    crud_log.add(
        db,
        current_user.id,
        current_user.username,
        "update",
        "member_suggestion",
        item.id,
        f"update member suggestion status to {item.status}",
    )
    return _serialize_suggestion(item)


@router.get("/members/suggestions/export")
def export_member_suggestions(
    keyword: str = "",
    status: str = "",
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    q = db.query(MemberSuggestion)
    if keyword:
        like = f"%{keyword.strip()}%"
        q = q.filter(
            or_(
                MemberSuggestion.member_name.ilike(like),
                MemberSuggestion.member_phone.ilike(like),
                MemberSuggestion.contact.ilike(like),
                MemberSuggestion.content.ilike(like),
            )
        )
    if status:
        q = q.filter(MemberSuggestion.status == status)

    items = q.order_by(MemberSuggestion.id.desc()).all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Member Suggestions"
    ws.append([
        "ID",
        "Member Name",
        "Member Phone",
        "Contact",
        "Content",
        "Status",
        "Created At",
        "Updated At",
    ])

    for item in items:
        ws.append([
            item.id,
            item.member_name or "",
            item.member_phone or "",
            item.contact or "",
            item.content,
            item.status,
            str(item.created_at) if item.created_at else "",
            str(item.updated_at) if item.updated_at else "",
        ])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=member_suggestions.xlsx"},
    )


@router.get("/members/binding-requests", response_model=PageMemberBindingRequest)
def list_member_binding_requests(
    keyword: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    items, total = crud_member.list_member_binding_requests(
        db,
        keyword=keyword,
        status=status,
        page=page,
        page_size=page_size,
    )
    return {"items": [_serialize_binding_request(item) for item in items], "total": total}


@router.post("/members/binding-requests/{request_id}/approve", response_model=MemberBindingRequestOut)
def approve_member_binding_request(
    request_id: int,
    data: MemberBindingRequestApproveIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = db.get(MemberBindingRequest, request_id)
    if not item:
        raise HTTPException(status_code=404, detail="binding request not found")
    if item.status != "pending":
        raise HTTPException(status_code=400, detail="binding request already handled")
    try:
        item = crud_member.approve_member_binding_request(
            db,
            item,
            donor_id=data.donor_id,
            admin_user_id=current_user.id,
            admin_note=data.admin_note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    crud_log.add(
        db,
        current_user.id,
        current_user.username,
        "approve",
        "member_binding_request",
        item.id,
        f"approve member binding request {item.id}",
    )
    return _serialize_binding_request(item)


@router.post("/members/binding-requests/{request_id}/reject", response_model=MemberBindingRequestOut)
def reject_member_binding_request(
    request_id: int,
    data: MemberBindingRequestRejectIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    item = db.get(MemberBindingRequest, request_id)
    if not item:
        raise HTTPException(status_code=404, detail="binding request not found")
    if item.status != "pending":
        raise HTTPException(status_code=400, detail="binding request already handled")
    item = crud_member.reject_member_binding_request(
        db,
        item,
        admin_user_id=current_user.id,
        admin_note=data.admin_note,
    )
    crud_log.add(
        db,
        current_user.id,
        current_user.username,
        "reject",
        "member_binding_request",
        item.id,
        f"reject member binding request {item.id}",
    )
    return _serialize_binding_request(item)


@router.put("/members/{member_id}", response_model=MemberPublicOut)
def update_member(
    member_id: int,
    data: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    member = crud_member.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="member not found")
    member = crud_member.update_member(db, member, data)
    crud_log.add(db, current_user.id, current_user.username, "update", "member", member.id, f"update member {member.phone}")
    return _serialize_member(db, member)


@router.get("/members/{member_id}/binding-code", response_model=MemberBindingCodeOut | None)
def get_member_binding_code(
    member_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    member = crud_member.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="member not found")
    item = crud_member.get_latest_pending_binding_code(db, member_id)
    if not item:
        return None
    return _serialize_binding_code(item)


@router.post("/members/{member_id}/binding-code", response_model=MemberBindingCodeOut, status_code=201)
def create_member_binding_code(
    member_id: int,
    data: MemberBindingCodeCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    member = crud_member.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="member not found")
    try:
        item = crud_member.create_binding_code(db, member, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    crud_log.add(db, current_user.id, current_user.username, "create", "member_binding_code", item.id, f"create binding code for member {member.phone}")
    return _serialize_binding_code(item)


@router.get("/members/donor-options", response_model=list[DonorOut])
def list_member_donor_options(
    keyword: str = "",
    page_size: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
):
    return crud_member.list_donor_candidates(db, keyword=keyword, page_size=page_size)
