import base64
import csv
import io
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, jsonify, render_template, request, session, redirect, url_for, make_response

from db.init_db import init_db
from utils.export_utils import generate_csv, generate_pdf, generate_category_summary_csv


def create_app() -> Flask:
    app = Flask(__name__)

    # Configuration
    app.config["DATABASE"] = os.environ.get("EXPENSE_TRACKER_DB", "budget.db")
    app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024  # 6MB uploads
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    init_db(app.config["DATABASE"])

    def get_db_connection() -> sqlite3.Connection:
        conn = sqlite3.connect(app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        return conn

    def get_current_user() -> str:
        """Get current user_id from session, default to 'default_user'"""
        return session.get('user_id', 'default_user')

    def login_required(f):
        """Decorator to ensure user is logged in"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                session['user_id'] = 'default_user'  # Auto-login for simplicity
            return f(*args, **kwargs)
        return decorated_function

    def parse_iso_date(date_str: str) -> str:
        # Expect YYYY-MM-DD from <input type="date">
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str

    def safe_sort(sort_value: str | None) -> str:
        return "ASC" if (sort_value or "").upper() == "ASC" else "DESC"

    def get_filtered_expenses(user_id: str, params: dict) -> list[dict]:
        """Helper function to fetch filtered expenses based on query parameters"""
        try:
            limit_raw = params.get("limit", "50")
            limit = max(1, min(int(limit_raw), 500))
        except ValueError:
            limit = 50

        month = (params.get("month") or "").strip() or None
        category_filter = (params.get("category") or "").strip() or None
        tag_filter = (params.get("tag") or "").strip() or None
        recurring_filter = params.get("recurring")  # "0", "1", or None
        search = (params.get("search") or "").strip() or None
        sort_by = (params.get("sort_by") or "date").strip().lower()
        sort_order = (params.get("sort_order") or "desc").strip().lower()
        min_amount_raw = (params.get("min_amount") or "").strip()
        max_amount_raw = (params.get("max_amount") or "").strip()
        start_date = (params.get("start_date") or "").strip() or None
        end_date = (params.get("end_date") or "").strip() or None

        # Validate sort_by
        valid_sort_fields = ["date", "amount", "category", "business"]
        if sort_by not in valid_sort_fields:
            sort_by = "date"
        
        # Validate sort_order
        sort_order = "ASC" if sort_order == "asc" else "DESC"
        
        # Parse amount filters
        min_amount = None
        max_amount = None
        try:
            if min_amount_raw:
                min_amount = float(min_amount_raw)
        except ValueError:
            pass
        
        try:
            if max_amount_raw:
                max_amount = float(max_amount_raw)
        except ValueError:
            pass

        with get_db_connection() as conn:
            query = """
                SELECT id, date, business, amount, category, description, photo, tags, is_recurring, notes
                FROM purchases
                WHERE user_id = ?
            """
            query_params = [user_id]

            if month:
                query += " AND strftime('%Y-%m', date) = ?"
                query_params.append(month)
            else:
                if start_date:
                    query += " AND date >= ?"
                    query_params.append(start_date)
                if end_date:
                    query += " AND date <= ?"
                    query_params.append(end_date)

            if category_filter:
                query += " AND category = ?"
                query_params.append(category_filter)

            if tag_filter:
                query += " AND (tags LIKE ? OR tags LIKE ? OR tags LIKE ? OR tags = ?)"
                query_params.extend([f"%,{tag_filter},%", f"{tag_filter},%", f"%,{tag_filter}", tag_filter])

            if recurring_filter in ["0", "1"]:
                query += " AND is_recurring = ?"
                query_params.append(int(recurring_filter))

            if search:
                query += " AND (business LIKE ? OR description LIKE ? OR category LIKE ?)"
                search_pattern = f"%{search}%"
                query_params.extend([search_pattern, search_pattern, search_pattern])

            if min_amount is not None:
                query += " AND amount >= ?"
                query_params.append(min_amount)

            if max_amount is not None:
                query += " AND amount <= ?"
                query_params.append(max_amount)

            query += f" ORDER BY {sort_by} {sort_order}"
            
            # Add secondary sort by id for consistency
            if sort_by != "date":
                query += f", date {sort_order}"
            query += f", id {sort_order}"
            
            query += " LIMIT ?"
            query_params.append(limit)

            rows = conn.execute(query, query_params).fetchall()

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
                    "tags": row["tags"] or "",
                    "is_recurring": row["is_recurring"],
                    "notes": row["notes"] or "",
                }
            )

        return purchases

    @app.route("/")
    @login_required
    def home():
        return render_template("index.html")

    @app.route("/add")
    @login_required
    def add_page():
        return render_template("add.html")

    @app.route("/recent")
    @login_required
    def recent_page():
        return render_template("recent.html")

    @app.route("/monthly")
    @login_required
    def monthly_page():
        return render_template("monthly.html")

    @app.route("/categories")
    @login_required
    def categories_page():
        return render_template("categories.html")

    @app.route("/budgets")
    @login_required
    def budgets_page():
        return render_template("budgets.html")

    @app.route("/logout")
    def logout():
        """Logout and clear session"""
        session.clear()
        return redirect(url_for('home'))

    # ==================== Expense Management ====================

    @app.route("/add", methods=["POST"])
    @login_required
    def add_purchase():
        user_id = get_current_user()
        date = (request.form.get("date") or "").strip()
        business = (request.form.get("business") or "").strip()
        amount_raw = (request.form.get("amount") or "").strip()
        category = (request.form.get("category") or "").strip()
        description = (request.form.get("description") or "").strip() or None
        tags = (request.form.get("tags") or "").strip() or None
        is_recurring = 1 if request.form.get("is_recurring") == "on" else 0
        notes = (request.form.get("notes") or "").strip() or None
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
                    INSERT INTO purchases (date, business, amount, category, description, photo, tags, is_recurring, notes, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (date, business, amount, category, description, photo_blob, tags, is_recurring, notes, user_id),
                )
                conn.commit()

                # Check budget cap
                budget_alert = check_budget_cap(conn, category, user_id, date)

            return jsonify({"success": True, "budget_alert": budget_alert})
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/expense/<int:expense_id>", methods=["GET"])
    @login_required
    def get_expense(expense_id: int):
        """Get a single expense by ID"""
        user_id = get_current_user()
        
        try:
            with get_db_connection() as conn:
                row = conn.execute(
                    """
                    SELECT id, date, business, amount, category, description, photo, tags, is_recurring, notes
                    FROM purchases
                    WHERE id = ? AND user_id = ?
                    """,
                    (expense_id, user_id)
                ).fetchone()
                
                if not row:
                    return jsonify({"success": False, "error": "Expense not found"}), 404
                
                photo_b64 = None
                if row["photo"]:
                    photo_b64 = base64.b64encode(row["photo"]).decode("utf-8")
                
                expense = {
                    "id": row["id"],
                    "date": row["date"],
                    "business": row["business"],
                    "amount": float(row["amount"]),
                    "category": row["category"],
                    "description": row["description"] or "",
                    "photo": photo_b64,
                    "tags": row["tags"] or "",
                    "is_recurring": row["is_recurring"],
                    "notes": row["notes"] or "",
                }
                
                return jsonify(expense)
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/update/<int:expense_id>", methods=["PUT", "PATCH"])
    @login_required
    def update_expense(expense_id: int):
        """Update an existing expense"""
        user_id = get_current_user()
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            date = (data.get("date") or "").strip()
            business = (data.get("business") or "").strip()
            amount_raw = (data.get("amount") or "").strip() if isinstance(data.get("amount"), str) else data.get("amount")
            category = (data.get("category") or "").strip()
            description = (data.get("description") or "").strip() or None
            tags = (data.get("tags") or "").strip() or None
            is_recurring = 1 if data.get("is_recurring") in [True, "true", "1", 1] else 0
            notes = (data.get("notes") or "").strip() or None
            photo_blob = None
            remove_photo = data.get("remove_photo", False)
        else:
            date = (request.form.get("date") or "").strip()
            business = (request.form.get("business") or "").strip()
            amount_raw = (request.form.get("amount") or "").strip()
            category = (request.form.get("category") or "").strip()
            description = (request.form.get("description") or "").strip() or None
            tags = (request.form.get("tags") or "").strip() or None
            is_recurring = 1 if request.form.get("is_recurring") == "on" else 0
            notes = (request.form.get("notes") or "").strip() or None
            photo_file = request.files.get("photo")
            remove_photo = request.form.get("remove_photo") == "true"
            
            photo_blob = None
            if photo_file and photo_file.filename:
                photo_blob = photo_file.read()

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
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid amount"}), 400

        try:
            with get_db_connection() as conn:
                # Check if expense exists and belongs to user
                existing = conn.execute(
                    "SELECT id FROM purchases WHERE id = ? AND user_id = ?",
                    (expense_id, user_id)
                ).fetchone()
                
                if not existing:
                    return jsonify({"success": False, "error": "Expense not found"}), 404
                
                # Build update query based on whether photo is being updated
                if remove_photo:
                    # Remove photo
                    result = conn.execute(
                        """
                        UPDATE purchases
                        SET date = ?, business = ?, amount = ?, category = ?, description = ?, 
                            photo = NULL, tags = ?, is_recurring = ?, notes = ?
                        WHERE id = ? AND user_id = ?
                        """,
                        (date, business, amount, category, description, tags, is_recurring, notes, expense_id, user_id)
                    )
                elif photo_blob is not None:
                    # Update with new photo
                    result = conn.execute(
                        """
                        UPDATE purchases
                        SET date = ?, business = ?, amount = ?, category = ?, description = ?, 
                            photo = ?, tags = ?, is_recurring = ?, notes = ?
                        WHERE id = ? AND user_id = ?
                        """,
                        (date, business, amount, category, description, photo_blob, tags, is_recurring, notes, expense_id, user_id)
                    )
                else:
                    # Update without touching photo
                    result = conn.execute(
                        """
                        UPDATE purchases
                        SET date = ?, business = ?, amount = ?, category = ?, description = ?, 
                            tags = ?, is_recurring = ?, notes = ?
                        WHERE id = ? AND user_id = ?
                        """,
                        (date, business, amount, category, description, tags, is_recurring, notes, expense_id, user_id)
                    )
                
                conn.commit()
                
                if result.rowcount == 0:
                    return jsonify({"success": False, "error": "Failed to update expense"}), 500
                
                # Check budget cap after update
                budget_alert = check_budget_cap(conn, category, user_id, date)
                
                return jsonify({"success": True, "message": "Expense updated successfully", "budget_alert": budget_alert})
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/delete/<int:expense_id>", methods=["DELETE"])
    @login_required
    def delete_expense(expense_id: int):
        """Delete an expense"""
        user_id = get_current_user()
        
        try:
            with get_db_connection() as conn:
                # Check if expense exists and belongs to user
                existing = conn.execute(
                    "SELECT id FROM purchases WHERE id = ? AND user_id = ?",
                    (expense_id, user_id)
                ).fetchone()
                
                if not existing:
                    return jsonify({"success": False, "error": "Expense not found"}), 404
                
                # Delete the expense
                result = conn.execute(
                    "DELETE FROM purchases WHERE id = ? AND user_id = ?",
                    (expense_id, user_id)
                )
                conn.commit()
                
                if result.rowcount == 0:
                    return jsonify({"success": False, "error": "Failed to delete expense"}), 500
                
                return jsonify({"success": True, "message": "Expense deleted successfully"})
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/month-data", methods=["GET"])
    @login_required
    def get_month_data():
        """Return purchases with enhanced filters."""
        user_id = get_current_user()

        try:
            purchases = get_filtered_expenses(user_id, request.args.to_dict())
            return jsonify(purchases)
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/overview-data", methods=["GET"])
    @login_required
    def get_overview_data():
        user_id = get_current_user()
        try:
            sort_by = safe_sort(request.args.get("sort"))
            start_date = (request.args.get("start_date") or "").strip() or None
            end_date = (request.args.get("end_date") or "").strip() or None

            # Validate date formats if provided
            if start_date:
                try:
                    parse_iso_date(start_date)
                except ValueError:
                    return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400

            if end_date:
                try:
                    parse_iso_date(end_date)
                except ValueError:
                    return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400

            with get_db_connection() as conn:
                query = """
                    SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total_amount
                    FROM purchases
                    WHERE user_id = ?
                """
                params = [user_id]

                if start_date:
                    query += " AND date >= ?"
                    params.append(start_date)

                if end_date:
                    query += " AND date <= ?"
                    params.append(end_date)

                query += f" GROUP BY month ORDER BY month {sort_by}"

                rows = conn.execute(query, params).fetchall()

            monthly_totals = [
                {"month": row["month"], "total": float(row["total_amount"] or 0)}
                for row in rows
            ]
            return jsonify(monthly_totals)
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/monthly-category-data", methods=["GET"])
    @login_required
    def get_monthly_category_data():
        user_id = get_current_user()
        try:
            month = (request.args.get("month") or "").strip() or None
            start_date = (request.args.get("start_date") or "").strip() or None
            end_date = (request.args.get("end_date") or "").strip() or None

            # Validate date formats if provided
            if start_date:
                try:
                    parse_iso_date(start_date)
                except ValueError:
                    return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400

            if end_date:
                try:
                    parse_iso_date(end_date)
                except ValueError:
                    return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400

            with get_db_connection() as conn:
                query = """
                    SELECT category, SUM(amount) AS category_amount
                    FROM purchases
                    WHERE user_id = ?
                """
                params = [user_id]

                # Month filter takes precedence for backward compatibility
                if month:
                    query += " AND strftime('%Y-%m', date) = ?"
                    params.append(month)
                else:
                    if start_date:
                        query += " AND date >= ?"
                        params.append(start_date)

                    if end_date:
                        query += " AND date <= ?"
                        params.append(end_date)

                query += " GROUP BY category ORDER BY category_amount DESC"

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

    # ==================== Category Management ====================

    @app.route("/api/categories", methods=["GET"])
    @login_required
    def get_categories():
        """Get all active custom categories for current user"""
        user_id = get_current_user()
        try:
            with get_db_connection() as conn:
                rows = conn.execute(
                    """
                    SELECT id, name, created_at
                    FROM custom_categories
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY name ASC
                    """,
                    (user_id,)
                ).fetchall()

            categories = [
                {"id": row["id"], "name": row["name"], "created_at": row["created_at"]}
                for row in rows
            ]
            return jsonify(categories)
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/categories", methods=["POST"])
    @login_required
    def create_category():
        """Create a new custom category"""
        user_id = get_current_user()
        data = request.get_json()
        name = (data.get("name") or "").strip()

        if not name:
            return jsonify({"success": False, "error": "Category name is required"}), 400

        try:
            with get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO custom_categories (name, user_id)
                    VALUES (?, ?)
                    """,
                    (name, user_id)
                )
                conn.commit()
            return jsonify({"success": True, "message": "Category created successfully"})
        except sqlite3.IntegrityError:
            return jsonify({"success": False, "error": "Category already exists"}), 400
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/categories/<int:category_id>", methods=["PUT"])
    @login_required
    def update_category(category_id: int):
        """Update an existing category"""
        user_id = get_current_user()
        data = request.get_json()
        name = (data.get("name") or "").strip()

        if not name:
            return jsonify({"success": False, "error": "Category name is required"}), 400

        try:
            with get_db_connection() as conn:
                result = conn.execute(
                    """
                    UPDATE custom_categories
                    SET name = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
                    WHERE id = ? AND user_id = ? AND is_active = 1
                    """,
                    (name, category_id, user_id)
                )
                conn.commit()

                if result.rowcount == 0:
                    return jsonify({"success": False, "error": "Category not found"}), 404

            return jsonify({"success": True, "message": "Category updated successfully"})
        except sqlite3.IntegrityError:
            return jsonify({"success": False, "error": "Category name already exists"}), 400
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/categories/<int:category_id>", methods=["DELETE"])
    @login_required
    def delete_category(category_id: int):
        """Soft delete a category"""
        user_id = get_current_user()

        try:
            with get_db_connection() as conn:
                # Check if category is being used
                usage = conn.execute(
                    """
                    SELECT COUNT(*) as count
                    FROM purchases p
                    JOIN custom_categories c ON p.category = c.name
                    WHERE c.id = ? AND p.user_id = ?
                    """,
                    (category_id, user_id)
                ).fetchone()

                if usage["count"] > 0:
                    return jsonify({
                        "success": False,
                        "error": "Cannot delete category that is in use. Please reassign expenses first."
                    }), 400

                result = conn.execute(
                    """
                    UPDATE custom_categories
                    SET is_active = 0, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
                    WHERE id = ? AND user_id = ?
                    """,
                    (category_id, user_id)
                )
                conn.commit()

                if result.rowcount == 0:
                    return jsonify({"success": False, "error": "Category not found"}), 404

            return jsonify({"success": True, "message": "Category deleted successfully"})
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # ==================== Budget Management ====================

    @app.route("/api/budgets", methods=["GET"])
    @login_required
    def get_budgets():
        """Get all budgets for current user"""
        user_id = get_current_user()
        try:
            with get_db_connection() as conn:
                rows = conn.execute(
                    """
                    SELECT id, category, budget_amount, period_type, created_at
                    FROM budgets
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY category ASC
                    """,
                    (user_id,)
                ).fetchall()

            budgets = [
                {
                    "id": row["id"],
                    "category": row["category"],
                    "budget_amount": float(row["budget_amount"]),
                    "period_type": row["period_type"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
            return jsonify(budgets)
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/budgets", methods=["POST"])
    @login_required
    def create_budget():
        """Create a new budget"""
        user_id = get_current_user()
        data = request.get_json()
        category = (data.get("category") or "").strip()
        budget_amount_raw = data.get("budget_amount")
        period_type = (data.get("period_type") or "monthly").strip()

        if not category or budget_amount_raw is None:
            return jsonify({"success": False, "error": "Category and budget amount are required"}), 400

        try:
            budget_amount = float(budget_amount_raw)
            if budget_amount < 0:
                raise ValueError
        except ValueError:
            return jsonify({"success": False, "error": "Invalid budget amount"}), 400

        try:
            with get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO budgets (category, budget_amount, period_type, user_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    (category, budget_amount, period_type, user_id)
                )
                conn.commit()
            return jsonify({"success": True, "message": "Budget created successfully"})
        except sqlite3.IntegrityError:
            return jsonify({"success": False, "error": "Budget already exists for this category"}), 400
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/budgets/<int:budget_id>", methods=["PUT"])
    @login_required
    def update_budget(budget_id: int):
        """Update an existing budget"""
        user_id = get_current_user()
        data = request.get_json()
        budget_amount_raw = data.get("budget_amount")

        if budget_amount_raw is None:
            return jsonify({"success": False, "error": "Budget amount is required"}), 400

        try:
            budget_amount = float(budget_amount_raw)
            if budget_amount < 0:
                raise ValueError
        except ValueError:
            return jsonify({"success": False, "error": "Invalid budget amount"}), 400

        try:
            with get_db_connection() as conn:
                result = conn.execute(
                    """
                    UPDATE budgets
                    SET budget_amount = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
                    WHERE id = ? AND user_id = ? AND is_active = 1
                    """,
                    (budget_amount, budget_id, user_id)
                )
                conn.commit()

                if result.rowcount == 0:
                    return jsonify({"success": False, "error": "Budget not found"}), 404

            return jsonify({"success": True, "message": "Budget updated successfully"})
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/budgets/<int:budget_id>", methods=["DELETE"])
    @login_required
    def delete_budget(budget_id: int):
        """Delete a budget"""
        user_id = get_current_user()

        try:
            with get_db_connection() as conn:
                result = conn.execute(
                    """
                    UPDATE budgets
                    SET is_active = 0, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
                    WHERE id = ? AND user_id = ?
                    """,
                    (budget_id, user_id)
                )
                conn.commit()

                if result.rowcount == 0:
                    return jsonify({"success": False, "error": "Budget not found"}), 404

            return jsonify({"success": True, "message": "Budget deleted successfully"})
        except sqlite3.Error as e:
            return jsonify({"success": False, "error": str(e)}), 500

    def check_budget_cap(conn: sqlite3.Connection, category: str, user_id: str, date: str) -> dict | None:
        """Check if spending exceeds budget cap for the category in the current month"""
        try:
            month = date[:7]  # Extract YYYY-MM
            
            # Get budget for this category
            budget_row = conn.execute(
                """
                SELECT budget_amount FROM budgets
                WHERE category = ? AND user_id = ? AND is_active = 1 AND period_type = 'monthly'
                """,
                (category, user_id)
            ).fetchone()

            if not budget_row:
                return None

            budget_amount = float(budget_row["budget_amount"])

            # Get total spending for this category this month
            spending_row = conn.execute(
                """
                SELECT SUM(amount) as total FROM purchases
                WHERE category = ? AND user_id = ? AND strftime('%Y-%m', date) = ?
                """,
                (category, user_id, month)
            ).fetchone()

            total_spent = float(spending_row["total"] or 0)

            if total_spent > budget_amount:
                return {
                    "exceeded": True,
                    "category": category,
                    "budget": budget_amount,
                    "spent": total_spent,
                    "over_by": total_spent - budget_amount
                }

            return None
        except Exception:
            return None

    @app.route("/api/budget-status", methods=["GET"])
    @login_required
    def get_budget_status():
        """Get budget status for all categories in current month"""
        user_id = get_current_user()
        month = (request.args.get("month") or datetime.now().strftime("%Y-%m")).strip()

        try:
            with get_db_connection() as conn:
                budgets = conn.execute(
                    """
                    SELECT category, budget_amount FROM budgets
                    WHERE user_id = ? AND is_active = 1 AND period_type = 'monthly'
                    """,
                    (user_id,)
                ).fetchall()

                status_list = []
                for budget in budgets:
                    category = budget["category"]
                    budget_amount = float(budget["budget_amount"])

                    spending = conn.execute(
                        """
                        SELECT SUM(amount) as total FROM purchases
                        WHERE category = ? AND user_id = ? AND strftime('%Y-%m', date) = ?
                        """,
                        (category, user_id, month)
                    ).fetchone()

                    total_spent = float(spending["total"] or 0)
                    percentage = (total_spent / budget_amount * 100) if budget_amount > 0 else 0

                    status_list.append({
                        "category": category,
                        "budget": budget_amount,
                        "spent": total_spent,
                        "remaining": budget_amount - total_spent,
                        "percentage": round(percentage, 2),
                        "exceeded": total_spent > budget_amount
                    })

            return jsonify(status_list)
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    # ==================== CSV Import/Export ====================

    @app.route("/api/export-csv", methods=["GET"])
    @login_required
    def export_csv_deprecated():
        """Export all expenses to CSV (deprecated, use /export/csv)"""
        user_id = get_current_user()

        try:
            with get_db_connection() as conn:
                rows = conn.execute(
                    """
                    SELECT date, business, amount, category, description, tags, is_recurring, notes
                    FROM purchases
                    WHERE user_id = ?
                    ORDER BY date DESC
                    """,
                    (user_id,)
                ).fetchall()

            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(["date", "business", "amount", "category", "description", "tags", "is_recurring", "notes"])
            
            # Write data
            for row in rows:
                writer.writerow([
                    row["date"],
                    row["business"],
                    row["amount"],
                    row["category"],
                    row["description"] or "",
                    row["tags"] or "",
                    "Yes" if row["is_recurring"] else "No",
                    row["notes"] or ""
                ])

            output.seek(0)
            
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename=expenses_{datetime.now().strftime('%Y%m%d')}.csv"}
            )

        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/import-csv", methods=["POST"])
    @login_required
    def import_csv():
        """Import expenses from CSV file"""
        user_id = get_current_user()

        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        if not file.filename.endswith(".csv"):
            return jsonify({"success": False, "error": "File must be a CSV"}), 400

        try:
            # Read CSV
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)

            imported_count = 0
            skipped_count = 0
            error_rows = []

            with get_db_connection() as conn:
                for idx, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        date = row.get("date", "").strip()
                        business = row.get("business", "").strip()
                        amount_raw = row.get("amount", "").strip()
                        category = row.get("category", "").strip()
                        description = row.get("description", "").strip() or None
                        tags = row.get("tags", "").strip() or None
                        is_recurring_raw = row.get("is_recurring", "").strip().lower()
                        is_recurring = 1 if is_recurring_raw in ["yes", "1", "true"] else 0
                        notes = row.get("notes", "").strip() or None

                        # Validate required fields
                        if not date or not business or not amount_raw or not category:
                            error_rows.append({"row": idx, "error": "Missing required fields"})
                            skipped_count += 1
                            continue

                        # Validate date
                        try:
                            parse_iso_date(date)
                        except ValueError:
                            error_rows.append({"row": idx, "error": "Invalid date format"})
                            skipped_count += 1
                            continue

                        # Validate amount
                        try:
                            amount = float(amount_raw)
                            if amount < 0:
                                raise ValueError
                        except ValueError:
                            error_rows.append({"row": idx, "error": "Invalid amount"})
                            skipped_count += 1
                            continue

                        # Check for duplicates
                        existing = conn.execute(
                            """
                            SELECT COUNT(*) as count FROM purchases
                            WHERE date = ? AND business = ? AND amount = ? AND category = ? AND user_id = ?
                            """,
                            (date, business, amount, category, user_id)
                        ).fetchone()

                        if existing["count"] > 0:
                            skipped_count += 1
                            continue

                        # Insert
                        conn.execute(
                            """
                            INSERT INTO purchases (date, business, amount, category, description, tags, is_recurring, notes, user_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (date, business, amount, category, description, tags, is_recurring, notes, user_id)
                        )
                        imported_count += 1

                    except Exception as e:
                        error_rows.append({"row": idx, "error": str(e)})
                        skipped_count += 1

                conn.commit()

            return jsonify({
                "success": True,
                "imported": imported_count,
                "skipped": skipped_count,
                "errors": error_rows[:10]  # Return first 10 errors
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # ==================== Export Endpoints ====================

    @app.route("/export/csv", methods=["GET"])
    @login_required
    def export_csv_filtered():
        """Export filtered expenses to CSV"""
        user_id = get_current_user()

        try:
            # Get filtered expenses using the helper function
            expenses = get_filtered_expenses(user_id, request.args.to_dict())

            # Generate filename based on filters
            month = request.args.get("month")
            start_date = request.args.get("start_date")
            end_date = request.args.get("end_date")
            
            if month:
                filename = f"expenses_{month}.csv"
            elif start_date and end_date:
                filename = f"expenses_{start_date}_to_{end_date}.csv"
            elif start_date:
                filename = f"expenses_from_{start_date}.csv"
            elif end_date:
                filename = f"expenses_until_{end_date}.csv"
            else:
                filename = f"all_expenses_{datetime.now().strftime('%Y%m%d')}.csv"

            # Generate CSV content
            csv_content = generate_csv(expenses)

            # Create response with proper headers
            response = make_response(csv_content)
            response.headers["Content-Type"] = "text/csv; charset=utf-8"
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"

            return response

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/export/pdf", methods=["GET"])
    @login_required
    def export_pdf_filtered():
        """Export filtered expenses to PDF"""
        user_id = get_current_user()

        try:
            # Get filtered expenses using the helper function
            expenses = get_filtered_expenses(user_id, request.args.to_dict())

            # Generate filename based on filters
            month = request.args.get("month")
            start_date = request.args.get("start_date")
            end_date = request.args.get("end_date")
            
            if month:
                filename = f"expense_report_{month}.pdf"
            elif start_date and end_date:
                filename = f"expense_report_{start_date}_to_{end_date}.pdf"
            elif start_date:
                filename = f"expense_report_from_{start_date}.pdf"
            elif end_date:
                filename = f"expense_report_until_{end_date}.pdf"
            else:
                filename = f"expense_report_{datetime.now().strftime('%Y%m%d')}.pdf"

            # Generate PDF content
            pdf_content = generate_pdf(expenses)

            # Create response with proper headers
            response = make_response(pdf_content)
            response.headers["Content-Type"] = "application/pdf"
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"

            return response

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/export/category-csv", methods=["GET"])
    @login_required
    def export_category_summary_csv():
        """Export category summary to CSV"""
        user_id = get_current_user()

        try:
            month = (request.args.get("month") or "").strip() or None
            start_date = (request.args.get("start_date") or "").strip() or None
            end_date = (request.args.get("end_date") or "").strip() or None

            # Validate date formats if provided
            if start_date:
                try:
                    parse_iso_date(start_date)
                except ValueError:
                    return jsonify({"success": False, "error": "Invalid start_date format. Use YYYY-MM-DD"}), 400

            if end_date:
                try:
                    parse_iso_date(end_date)
                except ValueError:
                    return jsonify({"success": False, "error": "Invalid end_date format. Use YYYY-MM-DD"}), 400

            # Fetch category summary data
            with get_db_connection() as conn:
                query = """
                    SELECT category, SUM(amount) AS total_amount, COUNT(*) as transaction_count
                    FROM purchases
                    WHERE user_id = ?
                """
                params = [user_id]

                # Month filter takes precedence
                if month:
                    query += " AND strftime('%Y-%m', date) = ?"
                    params.append(month)
                else:
                    if start_date:
                        query += " AND date >= ?"
                        params.append(start_date)
                    if end_date:
                        query += " AND date <= ?"
                        params.append(end_date)

                query += " GROUP BY category ORDER BY total_amount DESC"

                rows = conn.execute(query, params).fetchall()

            # Convert to list of dicts
            category_data = [
                {
                    "category": row["category"],
                    "total_amount": float(row["total_amount"]),
                    "transaction_count": row["transaction_count"]
                }
                for row in rows
            ]

            # Generate filename
            if month:
                filename = f"category_summary_{month}.csv"
            elif start_date and end_date:
                filename = f"category_summary_{start_date}_to_{end_date}.csv"
            elif start_date:
                filename = f"category_summary_from_{start_date}.csv"
            elif end_date:
                filename = f"category_summary_until_{end_date}.csv"
            else:
                filename = f"category_summary_{datetime.now().strftime('%Y%m%d')}.csv"

            # Generate CSV content
            csv_content = generate_category_summary_csv(category_data)

            # Create response with proper headers
            response = make_response(csv_content)
            response.headers["Content-Type"] = "text/csv; charset=utf-8"
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"

            return response

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))