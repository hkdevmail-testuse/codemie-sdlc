-- ================================================
-- Database Migration Script
-- From: Original expense_manager schema
-- To: Enhanced schema with security and features
-- Tickets: SCRUM-92, SCRUM-95, SCRUM-96, SCRUM-97
-- ================================================

USE expense_manager;

-- Step 1: Backup existing data
CREATE TABLE IF NOT EXISTS expenses_backup AS SELECT * FROM expenses;

-- Step 2: Create new tables

-- Users table (SCRUM-95: Security)
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(100) NOT NULL UNIQUE,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` ENUM('admin', 'user', 'viewer') NOT NULL DEFAULT 'user',
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_username` (`username`),
  INDEX `idx_email` (`email`),
  INDEX `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Categories table (SCRUM-96: Custom Categories)
CREATE TABLE IF NOT EXISTS `categories` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL UNIQUE,
  `description` TEXT,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_by` INT,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_name` (`name`),
  INDEX `idx_is_active` (`is_active`),
  FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Audit log table (SCRUM-95: Security)
CREATE TABLE IF NOT EXISTS `audit_log` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT,
  `action` VARCHAR(50) NOT NULL,
  `table_name` VARCHAR(50) NOT NULL,
  `record_id` INT,
  `old_value` TEXT,
  `new_value` TEXT,
  `ip_address` VARCHAR(45),
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_action` (`action`),
  INDEX `idx_created_at` (`created_at`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Step 3: Insert default users (SCRUM-95)
INSERT INTO `users` (`username`, `email`, `password_hash`, `role`, `is_active`) 
VALUES
('admin', 'admin@expense-tracker.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEgj4O', 'admin', TRUE),
('demo_user', 'demo@expense-tracker.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEgj4O', 'user', TRUE),
('migration_user', 'migration@expense-tracker.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEgj4O', 'user', TRUE)
ON DUPLICATE KEY UPDATE `email` = VALUES(`email`);

-- Step 4: Insert default categories (SCRUM-96)
INSERT INTO `categories` (`name`, `description`, `is_active`) 
VALUES
('Rent', 'Monthly rent or housing expenses', TRUE),
('Food', 'Groceries, dining, and food-related expenses', TRUE),
('Shopping', 'Retail purchases, clothes, gadgets', TRUE),
('Entertainment', 'Movies, concerts, leisure activities', TRUE),
('Other', 'Miscellaneous expenses', TRUE),
('Transportation', 'Gas, public transport, car maintenance', TRUE),
('Healthcare', 'Medical bills, medications, insurance', TRUE),
('Utilities', 'Electricity, water, internet, phone bills', TRUE),
('Education', 'Tuition, books, courses', TRUE),
('Travel', 'Vacation, trips, accommodation', TRUE)
ON DUPLICATE KEY UPDATE `description` = VALUES(`description`);

-- Step 5: Modify expenses table to add new columns
ALTER TABLE `expenses` 
ADD COLUMN IF NOT EXISTS `user_id` INT AFTER `id`,
ADD COLUMN IF NOT EXISTS `status` ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'approved' AFTER `notes`,
ADD COLUMN IF NOT EXISTS `receipt_path` VARCHAR(500) AFTER `status`,
ADD COLUMN IF NOT EXISTS `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER `created_at`,
MODIFY COLUMN `amount` DECIMAL(10, 2) NOT NULL CHECK (`amount` >= 0);

-- Step 6: Migrate existing expenses to migration_user
UPDATE `expenses` 
SET `user_id` = (SELECT id FROM users WHERE username = 'migration_user' LIMIT 1)
WHERE `user_id` IS NULL;

-- Step 7: Add foreign key constraints
ALTER TABLE `expenses`
ADD CONSTRAINT `fk_expenses_user_id` 
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
ADD CONSTRAINT `fk_expenses_category` 
  FOREIGN KEY (`category`) REFERENCES `categories`(`name`) ON UPDATE CASCADE;

-- Step 8: Add performance indexes (SCRUM-97)
CREATE INDEX IF NOT EXISTS `idx_user_id` ON `expenses`(`user_id`);
CREATE INDEX IF NOT EXISTS `idx_expense_date` ON `expenses`(`expense_date`);
CREATE INDEX IF NOT EXISTS `idx_category` ON `expenses`(`category`);
CREATE INDEX IF NOT EXISTS `idx_status` ON `expenses`(`status`);
CREATE INDEX IF NOT EXISTS `idx_user_date` ON `expenses`(`user_id`, `expense_date`);
CREATE INDEX IF NOT EXISTS `idx_date_category` ON `expenses`(`expense_date`, `category`);

-- Step 9: Create optimized views (SCRUM-97)
CREATE OR REPLACE VIEW `v_monthly_expense_summary` AS
SELECT 
    u.id AS user_id,
    u.username,
    DATE_FORMAT(e.expense_date, '%Y-%m') AS month,
    e.category,
    SUM(e.amount) AS total_amount,
    COUNT(e.id) AS transaction_count
FROM expenses e
JOIN users u ON e.user_id = u.id
WHERE e.status = 'approved'
GROUP BY u.id, u.username, DATE_FORMAT(e.expense_date, '%Y-%m'), e.category;

CREATE OR REPLACE VIEW `v_category_summary` AS
SELECT 
    e.user_id,
    u.username,
    e.category,
    SUM(e.amount) AS total_amount,
    AVG(e.amount) AS avg_amount,
    COUNT(e.id) AS transaction_count,
    MIN(e.expense_date) AS first_expense,
    MAX(e.expense_date) AS last_expense
FROM expenses e
JOIN users u ON e.user_id = u.id
WHERE e.status = 'approved'
GROUP BY e.user_id, u.username, e.category;

-- Step 10: Create stored procedures (SCRUM-97)
DROP PROCEDURE IF EXISTS `sp_get_expense_summary`;
DELIMITER $$
CREATE PROCEDURE `sp_get_expense_summary`(
    IN p_user_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        category,
        SUM(amount) AS total,
        COUNT(*) AS count,
        AVG(amount) AS average
    FROM expenses
    WHERE user_id = p_user_id
        AND expense_date BETWEEN p_start_date AND p_end_date
        AND status = 'approved'
    GROUP BY category
    ORDER BY total DESC;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS `sp_get_filtered_expenses`;
DELIMITER $$
CREATE PROCEDURE `sp_get_filtered_expenses`(
    IN p_user_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE,
    IN p_category VARCHAR(100),
    IN p_status VARCHAR(20),
    IN p_limit INT,
    IN p_offset INT
)
BEGIN
    SELECT 
        e.id,
        e.expense_date,
        e.amount,
        e.category,
        e.notes,
        e.status,
        e.receipt_path,
        e.created_at
    FROM expenses e
    WHERE e.user_id = p_user_id
        AND (p_start_date IS NULL OR e.expense_date >= p_start_date)
        AND (p_end_date IS NULL OR e.expense_date <= p_end_date)
        AND (p_category IS NULL OR e.category = p_category)
        AND (p_status IS NULL OR e.status = p_status)
    ORDER BY e.expense_date DESC, e.id DESC
    LIMIT p_limit OFFSET p_offset;
END$$
DELIMITER ;

-- Step 11: Analyze tables for optimization
ANALYZE TABLE users, categories, expenses, audit_log;

-- Step 12: Add migration audit log entry
INSERT INTO `audit_log` (`user_id`, `action`, `table_name`, `record_id`, `old_value`, `new_value`)
VALUES (1, 'MIGRATION', 'database', 0, 'original_schema', 'enhanced_schema');

-- Step 13: Verify migration
SELECT 
    'Migration Complete' AS status,
    (SELECT COUNT(*) FROM users) AS total_users,
    (SELECT COUNT(*) FROM categories) AS total_categories,
    (SELECT COUNT(*) FROM expenses) AS total_expenses,
    (SELECT COUNT(*) FROM audit_log) AS total_audit_logs;

-- ================================================
-- Migration Notes:
-- 1. Existing expenses are assigned to 'migration_user'
-- 2. All existing expenses are marked as 'approved'
-- 3. Category names in existing expenses must match new category table
-- 4. Original data is backed up in expenses_backup table
-- 5. Default password for all users: admin123 (change after login)
-- ================================================

-- Step 14: Validation queries (run separately to verify)
-- Check if all expenses have valid user_id:
-- SELECT COUNT(*) FROM expenses WHERE user_id IS NULL;
-- 
-- Check if all categories in expenses exist in categories table:
-- SELECT DISTINCT e.category 
-- FROM expenses e 
-- LEFT JOIN categories c ON e.category = c.name 
-- WHERE c.name IS NULL;
--
-- Check indexes:
-- SHOW INDEX FROM expenses;
-- SHOW INDEX FROM users;
-- SHOW INDEX FROM categories;

-- ================================================
-- Rollback Instructions (if needed):
-- ================================================
-- WARNING: Only use if migration fails
-- 
-- DROP TABLE IF EXISTS expenses;
-- RENAME TABLE expenses_backup TO expenses;
-- DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS categories;
-- DROP TABLE IF EXISTS audit_log;
-- DROP VIEW IF EXISTS v_monthly_expense_summary;
-- DROP VIEW IF EXISTS v_category_summary;
-- DROP PROCEDURE IF EXISTS sp_get_expense_summary;
-- DROP PROCEDURE IF EXISTS sp_get_filtered_expenses;

-- ================================================
-- End of Migration Script
-- ================================================
