from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import uuid4

import xlrd


YEAR_SHEET_START = 2020
YEAR_SHEET_END = 2026
YEAR_CHAR = "\u5e74"
IMPORT_TMP_DIR = Path(__file__).resolve().parents[2] / ".tmp" / "imports"


@dataclass
class NormalizedDonation:
    source_sheet: str
    source_row: int
    year: int
    donation_date: str
    donor_no: str
    donor_name: str
    target_name: str
    amount: str
    payment_method: str
    receipt_flag: bool
    remark: str


def decimal_from_cell(value: Any) -> Decimal:
    if value in ("", None):
        return Decimal("0")
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def text_from_cell(value: Any) -> str:
    if value in ("", None):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def normalize_target_name(name: str) -> str:
    aliases = {
        "天凯法律": "天凯法学",
        "东台杯专项": "东台杯素养赛",
    }
    return aliases.get(name.strip(), name.strip())


def year_sheet_names(book: xlrd.book.Book) -> list[tuple[int, str]]:
    names = set(book.sheet_names())
    result = []
    for year in range(YEAR_SHEET_START, YEAR_SHEET_END + 1):
        name = f"{year}{YEAR_CHAR}"
        if name in names:
            result.append((year, name))
    return result


def convert_workbook(book: xlrd.book.Book, source_file: str) -> dict[str, Any]:
    donations: list[NormalizedDonation] = []
    warnings: list[dict[str, Any]] = []
    target_names: set[str] = set()
    donors: dict[str, dict[str, str]] = {}

    for year, sheet_name in year_sheet_names(book):
        sheet = book.sheet_by_name(sheet_name)
        headers = [text_from_cell(sheet.cell_value(0, col)) for col in range(sheet.ncols)]

        for row_index in range(2, sheet.nrows):
            donor_no = text_from_cell(sheet.cell_value(row_index, 0))
            donor_name = text_from_cell(sheet.cell_value(row_index, 1))
            row_total = decimal_from_cell(sheet.cell_value(row_index, 2))

            if not donor_name:
                warnings.append({"sheet": sheet_name, "row": row_index + 1, "reason": "missing donor_name"})
                continue
            if row_total == 0:
                continue

            donors.setdefault(
                donor_name,
                {
                    "name": donor_name,
                    "type": "person",
                    "source_no": donor_no,
                },
            )

            project_sum = Decimal("0")
            for col_index in range(3, sheet.ncols):
                raw_target = headers[col_index] if col_index < len(headers) else ""
                target_name = normalize_target_name(raw_target)
                if not target_name:
                    continue
                amount = decimal_from_cell(sheet.cell_value(row_index, col_index))
                if amount == 0:
                    continue

                project_sum += amount
                target_names.add(target_name)
                donations.append(
                    NormalizedDonation(
                        source_sheet=sheet_name,
                        source_row=row_index + 1,
                        year=year,
                        donation_date=f"{year}-12-31",
                        donor_no=donor_no,
                        donor_name=donor_name,
                        target_name=target_name,
                        amount=str(amount),
                        payment_method="bank",
                        receipt_flag=False,
                        remark=f"Imported from {source_file} {sheet_name} row {row_index + 1}",
                    )
                )

            if project_sum != row_total:
                warnings.append(
                    {
                        "sheet": sheet_name,
                        "row": row_index + 1,
                        "donor_name": donor_name,
                        "reason": "project_sum_mismatch",
                        "row_total": str(row_total),
                        "project_sum": str(project_sum),
                        "difference": str(row_total - project_sum),
                    }
                )

    year_counter = Counter(item.year for item in donations)
    target_counter = Counter(item.target_name for item in donations)
    target_amounts: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    donor_amounts: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    year_amounts: dict[int, Decimal] = defaultdict(lambda: Decimal("0"))

    for item in donations:
        amount = Decimal(item.amount)
        target_amounts[item.target_name] += amount
        donor_amounts[item.donor_name] += amount
        year_amounts[item.year] += amount

    return {
        "meta": {
            "source_file": source_file,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "conversion_rule": "one non-zero yearly donor-project cell becomes one donation record",
            "donation_date_rule": "year-end placeholder date YYYY-12-31",
            "target_aliases": {
                "天凯法律": "天凯法学",
                "东台杯专项": "东台杯素养赛",
            },
        },
        "summary": {
            "donor_count": len(donors),
            "target_count": len(target_names),
            "donation_count": len(donations),
            "total_amount": str(sum((Decimal(item.amount) for item in donations), Decimal("0"))),
            "by_year": {
                str(year): {
                    "count": year_counter[year],
                    "amount": str(year_amounts[year]),
                }
                for year in sorted(year_amounts)
            },
            "top_targets": [
                {
                    "target_name": name,
                    "count": target_counter[name],
                    "amount": str(target_amounts[name]),
                }
                for name, _ in target_counter.most_common()
            ],
            "top_donors": [
                {
                    "donor_name": name,
                    "amount": str(amount),
                }
                for name, amount in sorted(donor_amounts.items(), key=lambda item: item[1], reverse=True)[:20]
            ],
            "warning_count": len(warnings),
        },
        "targets": [
            {
                "name": name,
                "description": f"Imported target from {source_file}: {name}",
                "status": "active",
            }
            for name in sorted(target_names)
        ],
        "donors": sorted(donors.values(), key=lambda item: item["name"]),
        "donations": [asdict(item) for item in donations],
        "warnings": warnings,
    }


def convert_xls_file(path: Path) -> dict[str, Any]:
    book = xlrd.open_workbook(path)
    return convert_workbook(book, path.name)


def convert_xls_bytes(content: bytes, filename: str) -> dict[str, Any]:
    book = xlrd.open_workbook(file_contents=content)
    return convert_workbook(book, filename)


def save_preview(data: dict[str, Any]) -> str:
    token = uuid4().hex
    IMPORT_TMP_DIR.mkdir(parents=True, exist_ok=True)
    path = IMPORT_TMP_DIR / f"{token}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return token


def load_preview(token: str) -> dict[str, Any]:
    path = IMPORT_TMP_DIR / f"{token}.json"
    if not path.exists():
        raise FileNotFoundError(token)
    return json.loads(path.read_text(encoding="utf-8"))

