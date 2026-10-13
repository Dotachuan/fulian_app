from __future__ import annotations

import argparse
from collections import defaultdict
from decimal import Decimal

from app.db.database import SessionLocal
from app.models.donation import Donation
from app.models.fund import FundUsageRecord


def donation_key(item: Donation) -> tuple:
    return (
        item.donor_id,
        item.target_id,
        item.donation_date,
        Decimal(item.amount),
        item.payment_method,
    )


def fund_record_key(item: FundUsageRecord) -> tuple:
    return (
        item.fund_id,
        item.record_date,
        item.project_desc,
        Decimal(item.income_amount),
        Decimal(item.expense_amount),
    )


def duplicate_groups(items: list, key_func) -> list[list]:
    grouped = defaultdict(list)
    for item in items:
        grouped[key_func(item)].append(item)
    return [group for group in grouped.values() if len(group) > 1]


def print_groups(label: str, groups: list[list], limit: int) -> None:
    print(f"\n{label}: {len(groups)} duplicate groups")
    for group in groups[:limit]:
        kept = group[0]
        removed = group[1:]
        print(
            f"  keep={kept.id}, remove={[item.id for item in removed]}, "
            f"date={getattr(kept, 'donation_date', getattr(kept, 'record_date', ''))}, "
            f"amount={getattr(kept, 'amount', getattr(kept, 'income_amount', ''))}"
        )
    if len(groups) > limit:
        print(f"  ... {len(groups) - limit} more groups not shown")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preview or repair duplicate donation rows created by annual Excel imports."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the repair. Without this flag the script is read-only.",
    )
    parser.add_argument("--limit", type=int, default=20, help="Maximum groups printed per table.")
    args = parser.parse_args()

    with SessionLocal() as db:
        donations = (
            db.query(Donation)
            .filter(Donation.is_deleted == False)
            .filter(Donation.status == "normal")
            .filter(Donation.remark.like("Imported from %"))
            .order_by(Donation.id.asc())
            .all()
        )
        donation_groups = duplicate_groups(donations, donation_key)
        duplicate_donations = [item for group in donation_groups for item in group[1:]]

        fund_records = (
            db.query(FundUsageRecord)
            .filter(FundUsageRecord.remark.like("Donation import income: Imported from %"))
            .order_by(FundUsageRecord.id.asc())
            .all()
        )
        fund_groups = duplicate_groups(fund_records, fund_record_key)
        duplicate_fund_records = [item for group in fund_groups for item in group[1:]]

        print_groups("Donations", donation_groups, args.limit)
        print_groups("Fund income records", fund_groups, args.limit)
        print(
            "\nSummary: "
            f"donation rows to soft-delete={len(duplicate_donations)}, "
            f"donation amount to remove={sum((Decimal(item.amount) for item in duplicate_donations), Decimal('0'))}, "
            f"fund rows to delete={len(duplicate_fund_records)}, "
            f"fund income to remove={sum((Decimal(item.income_amount) for item in duplicate_fund_records), Decimal('0'))}"
        )

        if not args.apply:
            print("\nDRY RUN ONLY. Review the output, back up MySQL, then rerun with --apply.")
            return

        for item in duplicate_donations:
            item.is_deleted = True
        for item in duplicate_fund_records:
            db.delete(item)
        db.commit()
        print("\nRepair committed successfully.")


if __name__ == "__main__":
    main()
