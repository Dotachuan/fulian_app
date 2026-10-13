from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.crud import donation as crud_donation, donor as crud_donor, fund as crud_fund, log as crud_log, target as crud_target
from app.models.donation import Donation
from app.models.donor import Donor
from app.models.target import Target
from app.models.user import User
from app.schemas.donation import DonationCreate
from app.schemas.donor import DonorCreate
from app.schemas.fund import FundCreate, FundUsageCreate
from app.schemas.target import TargetCreate
from app.services.donation_importer import convert_xls_bytes, load_preview, save_preview

router = APIRouter()


class DonationImportCommitIn(BaseModel):
    import_token: str
    duplicate_strategy: Literal["skip", "allow"] = "skip"


def _get_or_create_donor(db: Session, name: str) -> tuple[Donor, bool]:
    donor = db.query(Donor).filter(Donor.name == name, Donor.is_deleted == False).first()
    if donor:
        return donor, False
    donor = crud_donor.create(db, DonorCreate(name=name, type="person"))
    return donor, True


def _get_or_create_target(db: Session, name: str) -> tuple[Target, bool]:
    target = db.query(Target).filter(Target.name == name, Target.is_deleted == False).first()
    if target:
        return target, False
    target = crud_target.create(
        db,
        TargetCreate(
            name=name,
            description=f"Imported target: {name}",
        ),
    )
    return target, True


def _get_or_create_fund(db: Session, name: str):
    from app.models.fund import Fund

    fund = db.query(Fund).filter(Fund.name == name).first()
    if fund:
        return fund, False
    fund = crud_fund.create_fund(
        db,
        FundCreate(
            name=name,
            type="main" if name == "福莲主体" else "sub",
            description=f"Imported fund mapped from donation target: {name}",
            status="active",
            sort_order=0,
        ),
    )
    return fund, True


def _is_duplicate(db: Session, donor_id: int, target_id: int, item: dict) -> bool:
    # The remark contains the source row number, so it cannot be part of the
    # business key when duplicate rows exist in the imported workbook.
    return (
        db.query(Donation.id)
        .filter(Donation.is_deleted == False)
        .filter(Donation.donor_id == donor_id)
        .filter(Donation.target_id == target_id)
        .filter(Donation.donation_date == date.fromisoformat(item["donation_date"]))
        .filter(Donation.amount == Decimal(item["amount"]))
        .first()
        is not None
    )


def _fund_income_exists(db: Session, fund_id: int, item: dict, donor_name: str) -> bool:
    from app.models.fund import FundUsageRecord

    return (
        db.query(FundUsageRecord.id)
        .filter(FundUsageRecord.fund_id == fund_id)
        .filter(FundUsageRecord.record_date == date.fromisoformat(item["donation_date"]))
        .filter(FundUsageRecord.project_desc == f"捐赠收入 - {donor_name}")
        .filter(FundUsageRecord.income_amount == Decimal(item["amount"]))
        .filter(FundUsageRecord.expense_amount == Decimal("0"))
        .first()
        is not None
    )


def _create_fund_income(db: Session, fund_id: int, item: dict, donor_name: str) -> bool:
    if _fund_income_exists(db, fund_id, item, donor_name):
        return False
    crud_fund.create_usage_record(
        db,
        FundUsageCreate(
            fund_id=fund_id,
            record_date=date.fromisoformat(item["donation_date"]),
            project_desc=f"捐赠收入 - {donor_name}",
            income_amount=Decimal(item["amount"]),
            expense_amount=Decimal("0"),
            remark=f"Donation import income: {item.get('remark', '')}",
        ),
    )
    return True


@router.post("/imports/donations/preview")
async def preview_donation_import(
    file: UploadFile = File(...),
    _: User = Depends(require_roles("admin", "operator")),
):
    filename = file.filename or "upload.xls"
    if not filename.lower().endswith(".xls"):
        raise HTTPException(status_code=400, detail="Only .xls files are supported in this importer")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        data = convert_xls_bytes(content, filename)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse Excel file: {exc}") from exc

    token = save_preview(data)
    summary = data["summary"]
    return {
        "import_token": token,
        "summary": summary,
        "sample_donations": data["donations"][:10],
        "warnings": data["warnings"][:50],
    }


@router.post("/imports/donations/commit")
def commit_donation_import(
    data: DonationImportCommitIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
):
    try:
        preview = load_preview(data.import_token)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Import preview not found or expired")

    created_donors = 0
    created_targets = 0
    created_funds = 0
    imported = 0
    fund_income_created = 0
    fund_income_skipped = 0
    skipped_duplicates = 0
    failed: list[dict] = []
    donor_cache: dict[str, Donor] = {}
    target_cache: dict[str, Target] = {}

    for item in preview["donations"]:
        try:
            donor_name = item["donor_name"]
            target_name = item["target_name"]

            donor = donor_cache.get(donor_name)
            if not donor:
                donor, donor_created = _get_or_create_donor(db, donor_name)
                donor_cache[donor_name] = donor
                if donor_created:
                    created_donors += 1

            target = target_cache.get(target_name)
            if not target:
                target, target_created = _get_or_create_target(db, target_name)
                target_cache[target_name] = target
                if target_created:
                    created_targets += 1

            fund, fund_created = _get_or_create_fund(db, target_name)
            if fund_created:
                created_funds += 1

            if data.duplicate_strategy == "skip" and _is_duplicate(db, donor.id, target.id, item):
                if _create_fund_income(db, fund.id, item, donor_name):
                    fund_income_created += 1
                else:
                    fund_income_skipped += 1
                skipped_duplicates += 1
                continue

            donation = crud_donation.create(
                db,
                DonationCreate(
                    donation_date=date.fromisoformat(item["donation_date"]),
                    donor_id=donor.id,
                    target_id=target.id,
                    amount=Decimal(item["amount"]),
                    payment_method=item.get("payment_method") or "bank",
                    receipt_flag=bool(item.get("receipt_flag")),
                    remark=item.get("remark") or "",
                ),
                created_by=current_user.id,
            )
            imported += 1
            if _create_fund_income(db, fund.id, item, donor_name):
                fund_income_created += 1
            else:
                fund_income_skipped += 1
            crud_log.add(
                db,
                current_user.id,
                current_user.username,
                "create",
                "donation_import",
                donation.id,
                f"import donation {donation.donation_no}",
            )
        except Exception as exc:
            failed.append(
                {
                    "source_sheet": item.get("source_sheet"),
                    "source_row": item.get("source_row"),
                    "donor_name": item.get("donor_name"),
                    "target_name": item.get("target_name"),
                    "amount": item.get("amount"),
                    "error": str(exc),
                }
            )

    crud_log.add(
        db,
        current_user.id,
        current_user.username,
        "create",
        "donation_import",
        None,
        f"commit import token={data.import_token}, imported={imported}, skipped={skipped_duplicates}, failed={len(failed)}",
    )

    return {
        "created_donors": created_donors,
        "created_targets": created_targets,
        "created_funds": created_funds,
        "imported": imported,
        "fund_income_created": fund_income_created,
        "fund_income_skipped": fund_income_skipped,
        "skipped_duplicates": skipped_duplicates,
        "failed_count": len(failed),
        "failed": failed[:50],
        "source_summary": preview["summary"],
    }
