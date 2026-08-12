from __future__ import annotations

import io


def _add_expense(client, *, date: str, business: str, amount: str, category: str, description: str = ""):
    data = {
        "date": date,
        "business": business,
        "amount": amount,
        "category": category,
        "description": description,
    }
    # multipart/form-data expected by /add because it reads request.form and request.files
    return client.post("/add", data=data)


def test_add_expense_success_and_visible_in_recent(client):
    r = _add_expense(
        client,
        date="2026-08-01",
        business="Coffee Shop",
        amount="4.50",
        category="Restaurants",
        description="Latte",
    )
    assert r.status_code == 200
    body = r.get_json()
    assert body["success"] is True

    recent = client.get("/month-data?limit=10")
    assert recent.status_code == 200
    purchases = recent.get_json()
    assert isinstance(purchases, list)
    assert any(p["business"] == "Coffee Shop" and p["amount"] == 4.5 for p in purchases)


def test_add_expense_missing_required_fields_returns_400(client):
    r = _add_expense(client, date="", business="", amount="", category="", description="")
    assert r.status_code == 400
    body = r.get_json()
    assert body["success"] is False
    assert body["error"] == "Missing required fields"


def test_add_expense_invalid_date_returns_400(client):
    r = _add_expense(
        client,
        date="08-01-2026",
        business="Coffee Shop",
        amount="4.50",
        category="Restaurants",
        description="Latte",
    )
    assert r.status_code == 400
    body = r.get_json()
    assert body["success"] is False
    assert body["error"] == "Invalid date format"


def test_add_expense_invalid_amount_returns_400(client):
    r = _add_expense(
        client,
        date="2026-08-01",
        business="Coffee Shop",
        amount="-1",
        category="Restaurants",
        description="Latte",
    )
    assert r.status_code == 400
    body = r.get_json()
    assert body["success"] is False
    assert body["error"] == "Invalid amount"


def test_view_recent_expenses_returns_json_array(client):
    r = client.get("/month-data?limit=10")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_filter_expenses_by_month_returns_only_matching_rows(client):
    _add_expense(
        client,
        date="2026-08-10",
        business="August Purchase",
        amount="10",
        category="Misc",
        description="",
    )
    _add_expense(
        client,
        date="2026-07-10",
        business="July Purchase",
        amount="20",
        category="Misc",
        description="",
    )

    r = client.get("/month-data?month=2026-08&limit=50")
    assert r.status_code == 200
    purchases = r.get_json()
    assert any(p["business"] == "August Purchase" for p in purchases)
    assert all(p["date"].startswith("2026-08") for p in purchases)


def test_monthly_category_totals_include_expected_category(client):
    _add_expense(
        client,
        date="2026-08-03",
        business="Gas Station",
        amount="30",
        category="Gas/Car",
        description="",
    )

    r = client.get("/monthly-category-data?month=2026-08")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert any(d["category"] == "Gas/Car" for d in data)


def test_all_time_category_totals_highest_spend_category(client):
    _add_expense(
        client,
        date="2026-08-05",
        business="Big Store",
        amount="200",
        category="Furniture/Home",
        description="",
    )
    _add_expense(
        client,
        date="2026-08-06",
        business="Small Store",
        amount="50",
        category="Clothes",
        description="",
    )

    r = client.get("/monthly-category-data")
    assert r.status_code == 200
    totals = r.get_json()
    assert isinstance(totals, list)

    top = max(totals, key=lambda x: x["category_amount"])
    assert top["category"] == "Furniture/Home"


def test_update_endpoint_not_present_returns_404(client):
    # Current src/app.py does not implement update; ensure expectation is explicit.
    r = client.put("/update/1", json={"amount": 12.0})
    assert r.status_code == 404


def test_delete_endpoint_not_present_returns_404(client):
    r = client.delete("/delete/1")
    assert r.status_code == 404


def test_add_expense_with_photo_blob_returns_photo_in_month_data(client):
    img = io.BytesIO(b"fake-image-bytes")
    data = {
        "date": "2026-08-07",
        "business": "Photo Store",
        "amount": "9.99",
        "category": "Misc",
        "description": "Receipt",
        "photo": (img, "receipt.jpg"),
    }

    r = client.post("/add", data=data, content_type="multipart/form-data")
    assert r.status_code == 200
    assert r.get_json()["success"] is True

    recent = client.get("/month-data?month=2026-08&limit=10")
    purchases = recent.get_json()
    photo_row = next(p for p in purchases if p["business"] == "Photo Store")
    assert photo_row["photo"] is not None
