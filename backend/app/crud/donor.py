from datetime import datetime
import random
import string
from typing import Optional

from sqlalchemy.orm import Session

from app.models.donor import Donor
from app.schemas.donor import DonorCreate, DonorUpdate


def _generate_binding_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def get_list(db: Session, name: str = "", type_: str = "", page: int = 1, page_size: int = 20):
    q = db.query(Donor).filter(Donor.is_deleted == False)
    if name:
        q = q.filter(Donor.name.like(f"%{name}%"))
    if type_:
        q = q.filter(Donor.type == type_)
    total = q.count()
    items = q.order_by(Donor.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get(db: Session, donor_id: int) -> Optional[Donor]:
    return db.query(Donor).filter_by(id=donor_id, is_deleted=False).first()


def get_by_binding_code(db: Session, code: str) -> Optional[Donor]:
    return (
        db.query(Donor)
        .filter(Donor.is_deleted == False)
        .filter(Donor.binding_code == code)
        .first()
    )


def create(db: Session, data: DonorCreate) -> Donor:
    donor = Donor(**data.model_dump())
    db.add(donor)
    db.commit()
    db.refresh(donor)
    return donor


def update(db: Session, donor: Donor, data: DonorUpdate) -> Donor:
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(donor, k, v)
    db.commit()
    db.refresh(donor)
    return donor


def delete(db: Session, donor: Donor):
    donor.is_deleted = True
    db.commit()


def ensure_binding_code(db: Session, donor: Donor) -> Donor:
    if donor.binding_code:
        if not donor.binding_code_status:
            donor.binding_code_status = "bound" if donor.binding_bound_member_id else "active"
            db.commit()
            db.refresh(donor)
        return donor

    code = _generate_binding_code()
    while db.query(Donor).filter(Donor.binding_code == code).first():
        code = _generate_binding_code()
    donor.binding_code = code
    donor.binding_code_status = "bound" if donor.binding_bound_member_id else "active"
    db.commit()
    db.refresh(donor)
    return donor


def batch_generate_binding_codes(db: Session, only_missing: bool = True) -> dict:
    donors = db.query(Donor).filter(Donor.is_deleted == False).order_by(Donor.id.asc()).all()
    generated_count = 0
    reused_count = 0

    for donor in donors:
        if donor.binding_code:
            if donor.binding_code_status == "disabled" and not only_missing:
                donor.binding_code = None
            else:
                if not donor.binding_code_status:
                    donor.binding_code_status = "bound" if donor.binding_bound_member_id else "active"
                reused_count += 1
                continue

        code = _generate_binding_code()
        while db.query(Donor).filter(Donor.binding_code == code).first():
            code = _generate_binding_code()
        donor.binding_code = code
        donor.binding_code_status = "bound" if donor.binding_bound_member_id else "active"
        generated_count += 1

    db.commit()
    return {
        "generated_count": generated_count,
        "reused_count": reused_count,
        "total_count": len(donors),
    }


def set_binding_member(db: Session, donor: Donor, member_id: Optional[int]):
    donor.binding_bound_member_id = member_id
    donor.binding_bound_at = datetime.now() if member_id else None
    if donor.binding_code:
        donor.binding_code_status = "bound" if member_id else "active"
