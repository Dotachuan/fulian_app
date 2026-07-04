from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.crud import fund as crud_fund
from app.db.database import SessionLocal
from app.models.donation import Donation
from app.models.fund import Fund, FundUsageRecord
from app.schemas.fund import FundCreate, FundUsageCreate


def get_or_create_fund(db, name: str):
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


def income_exists(db, fund_id: int, donation: Donation) -> bool:
    return (
        db.query(FundUsageRecord.id)
        .filter(FundUsageRecord.fund_id == fund_id)
        .filter(FundUsageRecord.record_date == donation.donation_date)
        .filter(FundUsageRecord.project_desc == f"捐赠收入 - {donation.donor.name}")
        .filter(FundUsageRecord.income_amount == donation.amount)
        .filter(FundUsageRecord.expense_amount == Decimal("0"))
        .filter(FundUsageRecord.remark == f"Donation import income: {donation.remark or ''}")
        .first()
        is not None
    )


def main() -> None:
    created_funds = 0
    created_records = 0
    skipped_records = 0

    with SessionLocal() as db:
        donations = (
            db.query(Donation)
            .filter(Donation.is_deleted == False)
            .filter(Donation.remark.like("Imported from donate.xls%"))
            .all()
        )
        for donation in donations:
            if not donation.target or not donation.donor:
                skipped_records += 1
                continue
            fund, fund_created = get_or_create_fund(db, donation.target.name)
            if fund_created:
                created_funds += 1
            if income_exists(db, fund.id, donation):
                skipped_records += 1
                continue
            crud_fund.create_usage_record(
                db,
                FundUsageCreate(
                    fund_id=fund.id,
                    record_date=donation.donation_date,
                    project_desc=f"捐赠收入 - {donation.donor.name}",
                    income_amount=donation.amount,
                    expense_amount=Decimal("0"),
                    remark=f"Donation import income: {donation.remark or ''}",
                ),
            )
            created_records += 1

    print(f"Imported donation records scanned: {len(donations)}")
    print(f"Funds created: {created_funds}")
    print(f"Fund income records created: {created_records}")
    print(f"Skipped records: {skipped_records}")


if __name__ == "__main__":
    main()

