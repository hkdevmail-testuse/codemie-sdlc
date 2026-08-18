-- Enhanced Expense Manager Database Schema
-- Supports: Custom Categories, User Management, Role-Based Access Control, Performance Optimization

CREATE DATABASE IF NOT EXISTS `expense_manager` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `expense_manager`;

-- Drop existing tables if needed (for clean migration)
-- DROP TABLE IF EXISTS expenses;
-- DROP TABLE IF EXISTS categories;
-- DROP TABLE IF EXISTS users;

-- ================================================
-- Table: users
-- Purpose: Store user information with role-based access control
-- Enhancement: SCRUM-95 (Security)
-- ================================================
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

-- ================================================
-- Table: categories
-- Purpose: Store custom expense categories
-- Enhancement: SCRUM-96 (Custom Categories)
-- ================================================
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

-- Insert default categories
INSERT INTO `categories` (`name`, `description`, `is_active`) VALUES
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

-- ================================================
-- Table: expenses
-- Purpose: Store expense transactions with enhanced features
-- Enhancements: SCRUM-92 (Validation), SCRUM-95 (Security), SCRUM-97 (Performance)
-- ================================================
CREATE TABLE IF NOT EXISTS `expenses` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `expense_date` DATE NOT NULL,
  `amount` DECIMAL(10, 2) NOT NULL CHECK (`amount` >= 0),
  `category` VARCHAR(100) NOT NULL,
  `notes` TEXT,
  `status` ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'approved',
  `receipt_path` VARCHAR(500),
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_expense_date` (`expense_date`),
  INDEX `idx_category` (`category`),
  INDEX `idx_status` (`status`),
  INDEX `idx_user_date` (`user_id`, `expense_date`),
  INDEX `idx_date_category` (`expense_date`, `category`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`category`) REFERENCES `categories`(`name`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ================================================
-- Table: audit_log
-- Purpose: Track all changes for security and compliance
-- Enhancement: SCRUM-95 (Security)
-- ================================================
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

-- ================================================
-- Insert default admin user
-- Password: admin123 (hashed with bcrypt)
-- Enhancement: SCRUM-95 (Security)
-- Note: Change password after first login
-- ================================================
INSERT INTO `users` (`username`, `email`, `password_hash`, `role`, `is_active`) VALUES
('admin', 'admin@expense-tracker.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEgj4O', 'admin', TRUE),
('demo_user', 'demo@expense-tracker.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEgj4O', 'user', TRUE)
ON DUPLICATE KEY UPDATE `email` = VALUES(`email`);

-- ================================================
-- Migrate existing expenses data (if table exists)
-- Enhancement: Ensure backward compatibility
-- ================================================
-- This section will be handled separately in migration script

-- ================================================
-- Create Views for Analytics Performance
-- Enhancement: SCRUM-97 (Performance)
-- ================================================

-- View: Monthly expense summary per user
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

-- View: Category-wise spending
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

-- ================================================
-- Stored Procedures for Performance
-- Enhancement: SCRUM-97 (Performance)
-- ================================================

DELIMITER $$

-- Procedure: Get expense summary for date range
CREATE PROCEDURE IF NOT EXISTS `sp_get_expense_summary`(
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

-- Procedure: Get filtered expenses with pagination
CREATE PROCEDURE IF NOT EXISTS `sp_get_filtered_expenses`(
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

-- ================================================
-- Performance Optimization
-- Enhancement: SCRUM-97
-- ================================================

-- Analyze tables for query optimization
ANALYZE TABLE users, categories, expenses, audit_log;

-- ================================================
-- Security: Create application user with limited privileges
-- Enhancement: SCRUM-95 (Security)
-- ================================================

-- Note: Execute these commands separately with root privileges
-- CREATE USER IF NOT EXISTS 'expense_app'@'localhost' IDENTIFIED BY 'secure_password_here';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON expense_manager.* TO 'expense_app'@'localhost';
-- FLUSH PRIVILEGES;

-- ================================================
-- End of Enhanced Schema
-- ================================================
