import os
import sqlite3


def init_db(db_path: str) -> None:
    """Initialize the SQLite database using schema.sql."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_dir, "schema.sql")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    os.makedirs(os.path.dirname(db_path), exist_ok=True) if os.path.dirname(db_path) else None

    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_sql)
        conn.commit()


if __name__ == "__main__":
    db_path = os.environ.get("EXPENSE_TRACKER_DB", "budget.db")
    init_db(db_path)
    print(f"Initialized DB at {db_path}")
