from io import BytesIO

import openpyxl
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.crud import donor as crud_donor
from app.schemas.donor import (
    DonorBindingCodeBatchGenerateIn,
    DonorBindingCodeBatchGenerateOut,
    DonorCreate,
    DonorOut,
    DonorUpdate,
    PageDonor,
)

router = APIRouter()


def _serialize_donor(donor) -> DonorOut:
    return DonorOut(
        id=donor.id,
        name=donor.name,
        type=donor.type,
        phone=donor.phone,
        email=donor.email,
        address=donor.address,
        id_no=donor.id_no,
        remark=donor.remark,
        binding_code=donor.binding_code,
        binding_code_status=donor.binding_code_status,
        binding_bound_member_id=donor.binding_bound_member_id,
        binding_bound_member_name=donor.binding_member.name if donor.binding_member else None,
        binding_bound_at=donor.binding_bound_at,
        created_at=donor.created_at,
    )


@router.get("/donors/binding-codes/export")
def export_donor_binding_codes(
    name: str = "",
    type: str = "",
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    donors, _ = crud_donor.get_list(db, name=name, type_=type, page=1, page_size=100000)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Binding Codes"
    ws.append([
        "Donor Name",
        "Type",
        "Phone",
        "Binding Code",
        "Binding Status",
        "Bound Member",
        "Bound At",
        "Remark",
    ])

    for donor in donors:
        masked_phone = ""
        if donor.phone:
            masked_phone = str(donor.phone)
            if len(masked_phone) >= 7:
                masked_phone = f"{masked_phone[:3]}****{masked_phone[-4:]}"
        ws.append([
            donor.name,
            "person" if donor.type == "person" else "company",
            masked_phone,
            donor.binding_code or "",
            donor.binding_code_status or "missing",
            donor.binding_member.name if donor.binding_member else "",
            str(donor.binding_bound_at) if donor.binding_bound_at else "",
            donor.remark or "",
        ])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=donor_binding_codes.xlsx"},
    )


@router.post("/donors/binding-codes/batch-generate", response_model=DonorBindingCodeBatchGenerateOut)
def batch_generate_donor_binding_codes(
    data: DonorBindingCodeBatchGenerateIn,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    return crud_donor.batch_generate_binding_codes(db, only_missing=data.only_missing)


@router.get("/donors", response_model=PageDonor)
def list_donors(
    name: str = "",
    type: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    items, total = crud_donor.get_list(db, name=name, type_=type, page=page, page_size=page_size)
    return {"items": [_serialize_donor(item) for item in items], "total": total}


@router.get("/donors/{donor_id}", response_model=DonorOut)
def get_donor(donor_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    donor = crud_donor.get(db, donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="donor not found")
    return _serialize_donor(donor)


@router.post("/donors", response_model=DonorOut, status_code=201)
def create_donor(
    data: DonorCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    donor = crud_donor.create(db, data)
    return _serialize_donor(donor)


@router.put("/donors/{donor_id}", response_model=DonorOut)
def update_donor(
    donor_id: int,
    data: DonorUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "operator")),
):
    donor = crud_donor.get(db, donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="donor not found")
    donor = crud_donor.update(db, donor, data)
    return _serialize_donor(donor)


@router.delete("/donors/{donor_id}", status_code=204)
def delete_donor(
    donor_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    donor = crud_donor.get(db, donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="donor not found")
    crud_donor.delete(db, donor)
