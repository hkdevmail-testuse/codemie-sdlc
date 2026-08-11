-- SQLite schema for Personal Expense Tracker
-- Enhanced schema with custom categories, budgets, tags, and recurring expenses support
-- Keep this file idempotent.

PRAGMA foreign_keys = ON;

-- Main purchases table with enhanced fields
CREATE TABLE IF NOT EXISTS purchases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL, -- ISO-8601 (YYYY-MM-DD)
  business TEXT NOT NULL,
  amount REAL NOT NULL CHECK (amount >= 0),
  category TEXT NOT NULL,
  description TEXT,
  photo BLOB,
  tags TEXT, -- Comma-separated tags for filtering
  is_recurring INTEGER DEFAULT 0 CHECK (is_recurring IN (0, 1)), -- Boolean: 0=one-time, 1=recurring
  notes TEXT, -- Additional notes field for enhanced filtering
  user_id TEXT DEFAULT 'default_user', -- For future multi-user support
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

CREATE INDEX IF NOT EXISTS idx_purchases_date ON purchases(date);
CREATE INDEX IF NOT EXISTS idx_purchases_category ON purchases(category);
CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);
CREATE INDEX IF NOT EXISTS idx_purchases_is_recurring ON purchases(is_recurring);

-- Custom categories table
CREATE TABLE IF NOT EXISTS custom_categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  user_id TEXT DEFAULT 'default_user',
  is_active INTEGER DEFAULT 1 CHECK (is_active IN (0, 1)), -- Soft delete support
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(name, user_id)
);

CREATE INDEX IF NOT EXISTS idx_custom_categories_user_id ON custom_categories(user_id);
CREATE INDEX IF NOT EXISTS idx_custom_categories_is_active ON custom_categories(is_active);

-- Budgets table for category-based budget caps
CREATE TABLE IF NOT EXISTS budgets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category TEXT NOT NULL,
  budget_amount REAL NOT NULL CHECK (budget_amount >= 0),
  period_type TEXT DEFAULT 'monthly' CHECK (period_type IN ('monthly', 'yearly', 'custom')),
  user_id TEXT DEFAULT 'default_user',
  is_active INTEGER DEFAULT 1 CHECK (is_active IN (0, 1)),
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(category, user_id, period_type)
);

CREATE INDEX IF NOT EXISTS idx_budgets_user_id ON budgets(user_id);
CREATE INDEX IF NOT EXISTS idx_budgets_category ON budgets(category);
CREATE INDEX IF NOT EXISTS idx_budgets_is_active ON budgets(is_active);

-- Insert default categories (idempotent)
INSERT OR IGNORE INTO custom_categories (name, user_id) VALUES
  ('Groceries', 'default_user'),
  ('Furniture/Home', 'default_user'),
  ('Gas/Car', 'default_user'),
  ('Clothes', 'default_user'),
  ('School/Office Supplies', 'default_user'),
  ('Restaurants', 'default_user'),
  ('Misc', 'default_user');

-- User sessions table for simple authentication
CREATE TABLE IF NOT EXISTS user_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL UNIQUE,
  user_id TEXT DEFAULT 'default_user',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  expires_at TEXT NOT NULL,
  is_active INTEGER DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active);
