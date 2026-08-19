import base64
import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from db.init_db import init_db


def create_app() -> Flask:
    app = Flask(__name__)

    # Configuration
    app.config["DATABASE"] = os.environ.get("EXPENSE_TRACKER_DB", "budget.db")
    app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024  # 6MB uploads

    init_db(app.config["DATABASE"])

    def get_db_connection() -> sqlite3.Connection:
        conn = sqlite3.connect(app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        return conn

    def parse_iso_date(date_str: str) -> str:
        # Expect YYYY-MM-DD from <input type="date">
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str

    def safe_sort(sort_value: str | None) -> str:
        return "ASC" if (sort_value or "").upper() == "ASC" else "DESC"

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/add")
    def add_page():
        return render_template("add.html")

    @app.route("/recent")
    def recent_page():
        return render_template("recent.html")

    @app.route("/monthly")
    def monthly_page():
        return render_template("monthly.html")

    @app.route("/add", methods=["POST"])
    def add_purchase():
        date = (request.form.get("date") or "").strip()
        business = (request.form.get("business") or "").strip()
        amount_raw = (request.form.get("amount") or "").strip()
        category = (request.form.get("category") or "").strip()
        description = (request.form.get("description") or "").strip() or None
        photo_file = request.files.get("photo")

        if not date or not business or not amount_raw or not category:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        try:
            date = parse_iso_date(date)
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format"}), 400

        try:
            amount = float(amount_raw)
            if amount < 0:
                raise ValueError
        except ValueError:
            return jsonify({"success": False, "error": "Invalid amount"}), 400

        photo_blob = None
        if photo_file and photo_file.filename:
            photo_blob = photo_file.read()

        try:
            with get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO purchases (date, business, amount, category, description, photo)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (date, business, amount, category, description, photo_blob),
                )
                conn.commit()
            return jsonify({"success": True})
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/purchase/<int:purchase_id>", methods=["GET"])
    def get_purchase(purchase_id):
        """Get a single purchase by ID for editing."""
        try:
            with get_db_connection() as conn:
                row = conn.execute(
                    """
                    SELECT id, date, business, amount, category, description, photo
                    FROM purchases
                    WHERE id = ?
                    """,
                    (purchase_id,),
                ).fetchone()

            if not row:
                return jsonify({"error": "Purchase not found"}), 404

            photo_b64 = None
            if row["photo"]:
                photo_b64 = base64.b64encode(row["photo"]).decode("utf-8")

            purchase = {
                "id": row["id"],
                "date": row["date"],
                "business": row["business"],
                "amount": float(row["amount"]),
                "category": row["category"],
                "description": row["description"] or "",
                "photo": photo_b64,
            }

            return jsonify(purchase)
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/purchase/<int:purchase_id>", methods=["PUT"])
    def update_purchase(purchase_id):
        """Update an existing purchase."""
        data = request.get_json()

        date = (data.get("date") or "").strip()
        business = (data.get("business") or "").strip()
        amount_raw = data.get("amount")
        category = (data.get("category") or "").strip()
        description = (data.get("description") or "").strip() or None

        if not date or not business or amount_raw is None or not category:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        try:
            date = parse_iso_date(date)
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format"}), 400

        try:
            amount = float(amount_raw)
            if amount < 0:
                raise ValueError
        except ValueError:
            return jsonify({"success": False, "error": "Invalid amount"}), 400

        try:
            with get_db_connection() as conn:
                # Check if purchase exists
                existing = conn.execute(
                    "SELECT id FROM purchases WHERE id = ?", (purchase_id,)
                ).fetchone()

                if not existing:
                    return jsonify({"success": False, "error": "Purchase not found"}), 404

                # Update the purchase
                conn.execute(
                    """
                    UPDATE purchases
                    SET date = ?, business = ?, amount = ?, category = ?, description = ?,
                        updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
                    WHERE id = ?
                    """,
                    (date, business, amount, category, description, purchase_id),
                )
                conn.commit()

            return jsonify({"success": True, "message": "Purchase updated successfully"})
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/purchase/<int:purchase_id>", methods=["DELETE"])
    def delete_purchase(purchase_id):
        """Delete a purchase."""
        try:
            with get_db_connection() as conn:
                # Check if purchase exists
                existing = conn.execute(
                    "SELECT id FROM purchases WHERE id = ?", (purchase_id,)
                ).fetchone()

                if not existing:
                    return jsonify({"success": False, "error": "Purchase not found"}), 404

                # Delete the purchase
                conn.execute("DELETE FROM purchases WHERE id = ?", (purchase_id,))
                conn.commit()

            return jsonify({"success": True, "message": "Purchase deleted successfully"})
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/month-data", methods=["GET"])
    def get_month_data():
        """Return purchases with advanced filtering.

        Optional query params:
        - limit: int (default 50, max 500)
        - month: YYYY-MM to filter to a month
        - start_date: YYYY-MM-DD for date range
        - end_date: YYYY-MM-DD for date range
        - category: filter by category
        - business: filter by business name (partial match)
        - min_amount: minimum amount
        - max_amount: maximum amount
        """
        try:
            limit_raw = request.args.get("limit", "50")
            limit = max(1, min(int(limit_raw), 500))
        except ValueError:
            limit = 50

        month = (request.args.get("month") or "").strip() or None
        start_date = (request.args.get("start_date") or "").strip() or None
        end_date = (request.args.get("end_date") or "").strip() or None
        category = (request.args.get("category") or "").strip() or None
        business = (request.args.get("business") or "").strip() or None
        min_amount = request.args.get("min_amount")
        max_amount = request.args.get("max_amount")

        # Build dynamic query
        query = """
            SELECT id, date, business, amount, category, description, photo
            FROM purchases
            WHERE 1=1
        """
        params = []

        if month:
            query += " AND strftime('%Y-%m', date) = ?"
            params.append(month)
        elif start_date and end_date:
            query += " AND date BETWEEN ? AND ?"
            params.append(start_date)
            params.append(end_date)
        elif start_date:
            query += " AND date >= ?"
            params.append(start_date)
        elif end_date:
            query += " AND date <= ?"
            params.append(end_date)

        if category:
            query += " AND category = ?"
            params.append(category)

        if business:
            query += " AND business LIKE ?"
            params.append(f"%{business}%")

        if min_amount:
            try:
                query += " AND amount >= ?"
                params.append(float(min_amount))
            except ValueError:
                pass

        if max_amount:
            try:
                query += " AND amount <= ?"
                params.append(float(max_amount))
            except ValueError:
                pass

        query += " ORDER BY date DESC, id DESC LIMIT ?"
        params.append(limit)

        try:
            with get_db_connection() as conn:
                rows = conn.execute(query, params).fetchall()

            purchases: list[dict] = []
            for row in rows:
                photo_b64 = None
                if row["photo"]:
                    photo_b64 = base64.b64encode(row["photo"]).decode("utf-8")
                purchases.append(
                    {
                        "id": row["id"],
                        "date": row["date"],
                        "business": row["business"],
                        "amount": float(row["amount"]),
                        "category": row["category"],
                        "description": row["description"] or "",
                        "photo": photo_b64,
                    }
                )

            return jsonify(purchases)
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/overview-data", methods=["GET"])
    def get_overview_data():
        """Get monthly overview with optional date range filtering."""
        try:
            sort_by = safe_sort(request.args.get("sort"))
            start_date = (request.args.get("start_date") or "").strip() or None
            end_date = (request.args.get("end_date") or "").strip() or None

            query = """
                SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total_amount
                FROM purchases
                WHERE 1=1
            """
            params = []

            if start_date and end_date:
                query += " AND date BETWEEN ? AND ?"
                params.append(start_date)
                params.append(end_date)
            elif start_date:
                query += " AND date >= ?"
                params.append(start_date)
            elif end_date:
                query += " AND date <= ?"
                params.append(end_date)

            query += f" GROUP BY month ORDER BY month {sort_by}"

            with get_db_connection() as conn:
                rows = conn.execute(query, params).fetchall()

            monthly_totals = [
                {"month": row["month"], "total": float(row["total_amount"] or 0)}
                for row in rows
            ]
            return jsonify(monthly_totals)
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/monthly-category-data", methods=["GET"])
    def get_monthly_category_data():
        """Get category-wise spending with optional filtering."""
        try:
            month = (request.args.get("month") or "").strip() or None
            start_date = (request.args.get("start_date") or "").strip() or None
            end_date = (request.args.get("end_date") or "").strip() or None

            query = """
                SELECT category, SUM(amount) AS category_amount
                FROM purchases
                WHERE 1=1
            """
            params = []

            if month:
                query += " AND strftime('%Y-%m', date) = ?"
                params.append(month)
            elif start_date and end_date:
                query += " AND date BETWEEN ? AND ?"
                params.append(start_date)
                params.append(end_date)
            elif start_date:
                query += " AND date >= ?"
                params.append(start_date)
            elif end_date:
                query += " AND date <= ?"
                params.append(end_date)

            query += " GROUP BY category ORDER BY category_amount DESC"

            with get_db_connection() as conn:
                rows = conn.execute(query, params).fetchall()

            data = [
                {
                    "category": row["category"],
                    "category_amount": float(row["category_amount"] or 0),
                }
                for row in rows
            ]
            return jsonify(data)
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/categories", methods=["GET"])
    def get_categories():
        """Get list of all unique categories."""
        try:
            with get_db_connection() as conn:
                rows = conn.execute(
                    """
                    SELECT DISTINCT category
                    FROM purchases
                    ORDER BY category
                    """
                ).fetchall()

            categories = [row["category"] for row in rows]
            return jsonify(categories)
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
