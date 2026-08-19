-- SQLite schema for Personal Expense Tracker (Enhanced Version)
-- Keep this file idempotent.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS purchases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL, -- ISO-8601 (YYYY-MM-DD)
  business TEXT NOT NULL,
  amount REAL NOT NULL CHECK (amount >= 0),
  category TEXT NOT NULL,
  description TEXT,
  photo BLOB,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')) -- Tracks last update
);

CREATE INDEX IF NOT EXISTS idx_purchases_date ON purchases(date);
CREATE INDEX IF NOT EXISTS idx_purchases_category ON purchases(category);
CREATE INDEX IF NOT EXISTS idx_purchases_business ON purchases(business);

-- Migration: Add updated_at column if not exists (for existing databases)
-- SQLite doesn't support ALTER TABLE ADD COLUMN IF NOT EXISTS directly,
-- so this is handled in the init_db script
