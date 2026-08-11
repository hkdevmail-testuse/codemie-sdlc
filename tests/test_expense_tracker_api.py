from __future__ import annotations

import datetime as dt

import pytest
import requests


def _add_expense(
    base_url: str,
    *,
    date: str,
    business: str,
    amount: float,
    category: str,
    description: str | None = None,
    timeout: float = 10,
):
    data = {
        "date": date,
        "business": business,
        "amount": str(amount),
        "category": category,
        "description": description or "",
    }
    resp = requests.post(f"{base_url}/add", data=data, timeout=timeout)
    return resp


def _get_purchases(base_url: str, *, month: str | None = None, timeout: float = 10):
    params = {}
    if month:
        params["month"] = month
    resp = requests.get(f"{base_url}/month-data", params=params, timeout=timeout)
    return resp


@pytest.mark.usefixtures("api_is_up")
class TestExpenseTracker:
    def test_add_expense_success(self, base_url: str, http_timeout_seconds: float):
        resp = _add_expense(
            base_url,
            date="2026-08-01",
            business="Coffee Shop",
            amount=4.50,
            category="Restaurants",
            description="Latte",
            timeout=http_timeout_seconds,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True

    def test_add_expense_missing_required_fields(self, base_url: str, http_timeout_seconds: float):
        resp = requests.post(f"{base_url}/add", data={"date": "2026-08-01"}, timeout=http_timeout_seconds)
        assert resp.status_code == 400
        body = resp.json()
        assert body["success"] is False
        assert "Missing required fields" in body["error"]

    def test_view_recent_expenses_contains_added_expense(self, base_url: str, http_timeout_seconds: float):
        unique_business = f"Grocer-{dt.datetime.utcnow().timestamp()}"
        add = _add_expense(
            base_url,
            date="2026-08-02",
            business=unique_business,
            amount=25.10,
            category="Groceries",
            description="",
            timeout=http_timeout_seconds,
        )
        assert add.status_code == 200

        resp = _get_purchases(base_url, timeout=http_timeout_seconds)
        assert resp.status_code == 200
        purchases = resp.json()
        assert isinstance(purchases, list)
        assert any(p.get("business") == unique_business for p in purchases)

    def test_view_expenses_filtered_by_month(self, base_url: str, http_timeout_seconds: float):
        unique_business = f"Fuel-{dt.datetime.utcnow().timestamp()}"
        add = _add_expense(
            base_url,
            date="2026-08-03",
            business=unique_business,
            amount=40.00,
            category="Gas/Car",
            description="",
            timeout=http_timeout_seconds,
        )
        assert add.status_code == 200

        resp = _get_purchases(base_url, month="2026-08", timeout=http_timeout_seconds)
        assert resp.status_code == 200
        purchases = resp.json()
        assert any(p.get("business") == unique_business for p in purchases)

    def test_analyze_spending_date_range_category_wise_expected_endpoint_missing(
        self, base_url: str, http_timeout_seconds: float
    ):
        """Approved requirement expects date-range category-wise analytics.

        Current app exposes /monthly-category-data (month only) but no date-range endpoint.
        This test is expected to FAIL until the feature is implemented.
        """
        resp = requests.get(
            f"{base_url}/category-spend",
            params={"start": "2026-08-01", "end": "2026-08-31"},
            timeout=http_timeout_seconds,
        )
        # Expecting 200 per requirement; current app likely returns 404.
        assert resp.status_code == 200

    def test_update_expense_expected_endpoint_missing(self, base_url: str, http_timeout_seconds: float):
        """Approved requirement expects update expense.

        Current app has no update endpoint. This test is expected to FAIL until implemented.
        """
        # Attempt to update purchase id 1 (exists/not) - endpoint should exist regardless.
        resp = requests.put(
            f"{base_url}/purchase/1",
            json={"amount": 15.00, "description": "Notebook"},
            timeout=http_timeout_seconds,
        )
        assert resp.status_code in (200, 204)

    def test_visual_analytics_monthly_overview(self, base_url: str, http_timeout_seconds: float):
        resp = requests.get(f"{base_url}/overview-data", timeout=http_timeout_seconds)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        if data:
            assert set(data[0].keys()) >= {"month", "total"}
