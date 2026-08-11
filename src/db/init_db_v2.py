import os
import sqlite3


def init_db(db_path: str) -> None:
    """Initialize the SQLite database using schema.sql and handle migrations."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_dir, "schema.sql")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    os.makedirs(os.path.dirname(db_path), exist_ok=True) if os.path.dirname(db_path) else None

    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_sql)
        
        # Migration: Add updated_at column if it doesn't exist
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(purchases)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'updated_at' not in columns:
            try:
                conn.execute("""
                    ALTER TABLE purchases 
                    ADD COLUMN updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                """)
                print("Added updated_at column to purchases table")
            except sqlite3.OperationalError:
                pass  # Column might already exist
        
        conn.commit()


if __name__ == "__main__":
    db_path = os.environ.get("EXPENSE_TRACKER_DB", "budget.db")
    init_db(db_path)
    print(f"Initialized DB at {db_path}")
