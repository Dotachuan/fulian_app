from __future__ import annotations

from pathlib import Path
from decimal import Decimal
import sys
from uuid import uuid4

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.database import SessionLocal
from app.main import app
from app.models.invoice_request import InvoiceRequest


class AcceptanceFailure(RuntimeError):
    pass


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AcceptanceFailure(message)


def cleanup_invoice_request(request_id: int | None) -> None:
    if not request_id:
        return
    with SessionLocal() as db:
        item = db.get(InvoiceRequest, request_id)
        if item:
            db.delete(item)
            db.commit()


def main() -> None:
    suffix = uuid4().hex[:8]
    created: dict[str, int] = {}
    donor_name = f"Portal Donor {suffix}"
    fund_name = f"Portal Main Fund {suffix}"

    with TestClient(app) as client:
        login = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@123"},
        )
        ensure(login.status_code == 200, f"login failed: {login.text}")
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        try:
            donor = client.post(
                "/api/v1/donors",
                json={
                    "name": donor_name,
                    "type": "person",
                    "phone": "13800000000",
                    "email": "portal@example.com",
                },
                headers=headers,
            )
            ensure(donor.status_code == 201, f"create donor failed: {donor.text}")
            created["donor_id"] = donor.json()["id"]

            target = client.post(
                "/api/v1/targets",
                json={"name": f"Portal Target {suffix}", "description": "portal acceptance target"},
                headers=headers,
            )
            ensure(target.status_code == 201, f"create target failed: {target.text}")
            created["target_id"] = target.json()["id"]

            donation = client.post(
                "/api/v1/donations",
                json={
                    "donation_date": "2026-04-20",
                    "donor_id": created["donor_id"],
                    "target_id": created["target_id"],
                    "amount": "520.00",
                    "payment_method": "bank",
                    "receipt_flag": True,
                    "receipt_no": f"PORTAL-RCPT-{suffix}",
                    "remark": "portal acceptance donation",
                },
                headers=headers,
            )
            ensure(donation.status_code == 201, f"create donation failed: {donation.text}")
            created["donation_id"] = donation.json()["id"]

            public_donations = client.get(
                "/api/v1/public/donations/query",
                params={"donor_name": donor_name, "year": 2026, "page": 1, "page_size": 10},
            )
            ensure(public_donations.status_code == 200, f"public donation query failed: {public_donations.text}")
            donation_items = public_donations.json()["items"]
            ensure(len(donation_items) == 1, "public donation query should return one test item")
            ensure(donation_items[0]["donor_name"] == donor_name, "public donation donor_name mismatch")
            ensure("phone" not in donation_items[0], "public donation response should not expose phone")

            public_summary = client.get(
                "/api/v1/public/donations/summary",
                params={"donor_name": donor_name, "year": 2026},
            )
            ensure(public_summary.status_code == 200, f"public donation summary failed: {public_summary.text}")
            summary = public_summary.json()
            ensure(summary["total_count"] == 1, "summary total_count mismatch")
            ensure(Decimal(str(summary["total_amount"])) == Decimal("520.00"), "summary total_amount mismatch")

            fund = client.post(
                "/api/v1/funds",
                json={
                    "name": fund_name,
                    "type": "main",
                    "description": "Portal acceptance fund",
                    "status": "active",
                    "sort_order": 1,
                },
                headers=headers,
            )
            ensure(fund.status_code == 201, f"create fund failed: {fund.text}")
            created["fund_id"] = fund.json()["id"]

            usage_income = client.post(
                "/api/v1/fund-usage-records",
                json={
                    "fund_id": created["fund_id"],
                    "record_date": "2026-04-20",
                    "project_desc": "Acceptance income",
                    "income_amount": "1000.00",
                    "expense_amount": "0.00",
                    "remark": "portal acceptance income",
                },
                headers=headers,
            )
            ensure(usage_income.status_code == 201, f"create income record failed: {usage_income.text}")
            created["usage_income_id"] = usage_income.json()["id"]

            usage_expense = client.post(
                "/api/v1/fund-usage-records",
                json={
                    "fund_id": created["fund_id"],
                    "record_date": "2026-04-21",
                    "project_desc": "Acceptance expense",
                    "income_amount": "0.00",
                    "expense_amount": "300.00",
                    "remark": "portal acceptance expense",
                },
                headers=headers,
            )
            ensure(usage_expense.status_code == 201, f"create expense record failed: {usage_expense.text}")
            created["usage_expense_id"] = usage_expense.json()["id"]

            public_funds = client.get("/api/v1/public/funds")
            ensure(public_funds.status_code == 200, f"public funds failed: {public_funds.text}")
            ensure(
                any(item["id"] == created["fund_id"] for item in public_funds.json()["items"]),
                "created fund not found in public fund list",
            )

            public_usage = client.get(
                f"/api/v1/public/funds/{created['fund_id']}/usage",
                params={"page": 1, "page_size": 10},
            )
            ensure(public_usage.status_code == 200, f"public fund usage failed: {public_usage.text}")
            usage = public_usage.json()
            ensure(Decimal(str(usage["summary"]["total_income"])) == Decimal("1000.00"), "fund income mismatch")
            ensure(Decimal(str(usage["summary"]["total_expense"])) == Decimal("300.00"), "fund expense mismatch")
            ensure(Decimal(str(usage["summary"]["balance"])) == Decimal("700.00"), "fund balance mismatch")
            ensure(usage["total"] == 2, "fund usage total mismatch")

            invoice = client.post(
                "/api/v1/public/invoice-requests",
                json={
                    "donor_name": donor_name,
                    "amount": "520.00",
                    "donation_date": "2026-04-20",
                    "email": "portal@example.com",
                    "phone": "13800000000",
                    "identity_no": f"ID-{suffix}",
                    "remark": "portal acceptance invoice",
                },
            )
            ensure(invoice.status_code == 201, f"create public invoice failed: {invoice.text}")
            created["invoice_id"] = invoice.json()["id"]
            ensure(invoice.json()["status"] == "pending", "invoice should start as pending")

            invoice_list = client.get(
                "/api/v1/invoice-requests",
                params={"donor_name": donor_name, "page": 1, "page_size": 10},
                headers=headers,
            )
            ensure(invoice_list.status_code == 200, f"invoice list failed: {invoice_list.text}")
            ensure(invoice_list.json()["total"] >= 1, "invoice list should include created request")

            invoice_update = client.put(
                f"/api/v1/invoice-requests/{created['invoice_id']}",
                json={"status": "processed", "remark": "processed by acceptance"},
                headers=headers,
            )
            ensure(invoice_update.status_code == 200, f"invoice update failed: {invoice_update.text}")
            ensure(invoice_update.json()["status"] == "processed", "invoice status update mismatch")

            invoice_export = client.get(
                "/api/v1/invoice-requests/export",
                params={"donor_name": donor_name},
                headers=headers,
            )
            ensure(invoice_export.status_code == 200, f"invoice export failed: {invoice_export.text}")
            ensure(
                "spreadsheetml" in invoice_export.headers.get("content-type", ""),
                "invoice export should return xlsx content",
            )
            ensure(len(invoice_export.content) > 0, "invoice export body should not be empty")

            print("Portal acceptance passed.")
        finally:
            if "invoice_id" in created:
                cleanup_invoice_request(created.get("invoice_id"))
            if "usage_income_id" in created:
                client.delete(f"/api/v1/fund-usage-records/{created['usage_income_id']}", headers=headers)
            if "usage_expense_id" in created:
                client.delete(f"/api/v1/fund-usage-records/{created['usage_expense_id']}", headers=headers)
            if "fund_id" in created:
                client.delete(f"/api/v1/funds/{created['fund_id']}", headers=headers)
            if "donation_id" in created:
                client.delete(f"/api/v1/donations/{created['donation_id']}", headers=headers)
            if "donor_id" in created:
                client.delete(f"/api/v1/donors/{created['donor_id']}", headers=headers)
            if "target_id" in created:
                client.delete(f"/api/v1/targets/{created['target_id']}", headers=headers)


if __name__ == "__main__":
    main()

