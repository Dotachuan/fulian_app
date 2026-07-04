import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.donation_importer import convert_xls_file


def write_json(data: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert donate.xls yearly project details to normalized JSON.")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parents[2] / "donate.xls"),
        help="Path to donate.xls",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parents[2] / "backend" / ".tmp" / "donate.normalized.json"),
        help="Output JSON path",
    )
    args = parser.parse_args()

    data = convert_xls_file(Path(args.input))
    write_json(data, Path(args.output))

    summary = data["summary"]
    print(f"Output: {args.output}")
    print(f"Donors: {summary['donor_count']}")
    print(f"Targets: {summary['target_count']}")
    print(f"Donations: {summary['donation_count']}")
    print(f"Total amount: {summary['total_amount']}")
    print(f"Warnings: {summary['warning_count']}")


if __name__ == "__main__":
    main()
