from __future__ import annotations

from pathlib import Path
import sys
from uuid import uuid4

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app


class SmokeFailure(RuntimeError):
    pass


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def main() -> None:
    suffix = uuid4().hex[:8]
    created: dict[str, int] = {}

    with TestClient(app) as client:
        login = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@123"},
        )
        ensure(login.status_code == 200, f"login failed: {login.text}")
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        try:
            donor = client.post(
                "/api/v1/donors",
                json={"name": f"验收捐款人-{suffix}", "type": "person"},
                headers=headers,
            )
            ensure(donor.status_code == 201, f"create donor failed: {donor.text}")
            created["donor_id"] = donor.json()["id"]

            target = client.post(
                "/api/v1/targets",
                json={"name": f"验收目标-{suffix}", "description": "smoke acceptance"},
                headers=headers,
            )
            ensure(target.status_code == 201, f"create target failed: {target.text}")
            created["target_id"] = target.json()["id"]

            donation = client.post(
                "/api/v1/donations",
                json={
                    "donation_date": "2026-03-21",
                    "donor_id": created["donor_id"],
                    "target_id": created["target_id"],
                    "amount": "1234.56",
                    "payment_method": "bank",
                    "receipt_flag": True,
                    "receipt_no": f"RCPT-{suffix}",
                    "remark": "smoke acceptance",
                },
                headers=headers,
            )
            ensure(donation.status_code == 201, f"create donation failed: {donation.text}")
            created["donation_id"] = donation.json()["id"]

            donation_list_clean = client.get(
                "/api/v1/donations",
                params={"page": 1, "page_size": 20, "donor_name": suffix},
                headers=headers,
            )
            ensure(donation_list_clean.status_code == 200, f"list donations failed: {donation_list_clean.text}")
            ensure(
                any(item["id"] == created["donation_id"] for item in donation_list_clean.json()["items"]),
                "created donation not found in list",
            )

            donation_detail = client.get(f"/api/v1/donations/{created['donation_id']}", headers=headers)
            ensure(donation_detail.status_code == 200, f"donation detail failed: {donation_detail.text}")

            logs = client.get("/api/v1/logs", params={"page": 1, "page_size": 20}, headers=headers)
            ensure(logs.status_code == 200, f"logs failed: {logs.text}")
            ensure(logs.json()["total"] >= 1, "logs should contain at least one item")

            stats_overview = client.get("/api/v1/stats/overview", headers=headers)
            ensure(stats_overview.status_code == 200, f"stats overview failed: {stats_overview.text}")

            stats_trend = client.get("/api/v1/stats/trend", params={"period": "month"}, headers=headers)
            ensure(stats_trend.status_code == 200, f"stats trend failed: {stats_trend.text}")

            stats_target = client.get("/api/v1/stats/by-target", headers=headers)
            ensure(stats_target.status_code == 200, f"stats by target failed: {stats_target.text}")

            stats_method = client.get("/api/v1/stats/by-method", headers=headers)
            ensure(stats_method.status_code == 200, f"stats by method failed: {stats_method.text}")

            export_resp = client.get(
                "/api/v1/donations/export",
                params={"donor_name": suffix},
                headers=headers,
            )
            ensure(export_resp.status_code == 200, f"export failed: {export_resp.text}")
            ensure(
                "spreadsheetml" in export_resp.headers.get("content-type", ""),
                "export content-type is not xlsx",
            )
            ensure(len(export_resp.content) > 0, "export body should not be empty")

            print("Smoke acceptance passed.")
        finally:
            if "donation_id" in created:
                client.delete(f"/api/v1/donations/{created['donation_id']}", headers=headers)
            if "donor_id" in created:
                client.delete(f"/api/v1/donors/{created['donor_id']}", headers=headers)
            if "target_id" in created:
                client.delete(f"/api/v1/targets/{created['target_id']}", headers=headers)


if __name__ == "__main__":
    main()
