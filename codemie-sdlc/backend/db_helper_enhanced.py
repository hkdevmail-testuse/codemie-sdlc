"""
Enhanced Database Helper Module
Implements: Validation, Filtering, Security, Custom Categories, Performance Optimization
Tickets: SCRUM-92, SCRUM-93, SCRUM-95, SCRUM-96, SCRUM-97
"""

import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
import bcrypt
import re
from decimal import Decimal, InvalidOperation
from logging_setup import setup_logger

logger = setup_logger('db_helper_enhanced')

# Database connection pool for performance optimization (SCRUM-97)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "expense_manager",
    "pool_name": "expense_pool",
    "pool_size": 10,
    "pool_reset_session": True
}

try:
    connection_pool = pooling.MySQLConnectionPool(**DB_CONFIG)
    logger.info("Database connection pool created successfully")
except mysql.connector.Error as e:
    logger.error(f"Error creating connection pool: {e}")
    connection_pool = None


@contextmanager
def get_db_cursor(commit=False, dictionary=True):
    """
    Context manager for database operations with connection pooling
    Enhancement: SCRUM-97 (Performance)
    """
    connection = None
    cursor = None
    try:
        if connection_pool:
            connection = connection_pool.get_connection()
        else:
            connection = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"]
            )
        
        cursor = connection.cursor(dictionary=dictionary)
        yield cursor
        
        if commit:
            connection.commit()
            logger.debug("Transaction committed successfully")
    except mysql.connector.Error as e:
        if connection:
            connection.rollback()
            logger.error(f"Database error, rolled back transaction: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ================================================
# SCRUM-95: Security Functions
# ================================================

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt
    Enhancement: SCRUM-95 (Security)
    """
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify password against hash
    Enhancement: SCRUM-95 (Security)
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user and return user info
    Enhancement: SCRUM-95 (Security)
    """
    logger.info(f"Authentication attempt for user: {username}")
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """SELECT id, username, email, password_hash, role, is_active 
                   FROM users WHERE username = %s""",
                (username,)
            )
            user = cursor.fetchone()
            
            if user and user['is_active'] and verify_password(password, user['password_hash']):
                logger.info(f"User {username} authenticated successfully")
                # Don't return password hash
                del user['password_hash']
                return user
            
            logger.warning(f"Authentication failed for user: {username}")
            return None
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None


def create_user(username: str, email: str, password: str, role: str = 'user') -> Optional[int]:
    """
    Create a new user
    Enhancement: SCRUM-95 (Security)
    """
    logger.info(f"Creating new user: {username}")
    try:
        password_hash = hash_password(password)
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """INSERT INTO users (username, email, password_hash, role, is_active)
                   VALUES (%s, %s, %s, %s, TRUE)""",
                (username, email, password_hash, role)
            )
            user_id = cursor.lastrowid
            logger.info(f"User created successfully with ID: {user_id}")
            return user_id
    except mysql.connector.IntegrityError as e:
        logger.error(f"User creation failed - duplicate entry: {e}")
        return None
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None


def check_user_permission(user_id: int, required_role: str = 'user') -> bool:
    """
    Check if user has required role
    Enhancement: SCRUM-95 (Security)
    """
    role_hierarchy = {'admin': 3, 'user': 2, 'viewer': 1}
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT role FROM users WHERE id = %s AND is_active = TRUE", (user_id,))
            result = cursor.fetchone()
            if result:
                user_role = result['role']
                return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
        return False
    except Exception as e:
        logger.error(f"Error checking permissions: {e}")
        return False


def add_audit_log(user_id: Optional[int], action: str, table_name: str, 
                  record_id: Optional[int] = None, old_value: Optional[str] = None,
                  new_value: Optional[str] = None, ip_address: Optional[str] = None):
    """
    Add entry to audit log
    Enhancement: SCRUM-95 (Security)
    """
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """INSERT INTO audit_log (user_id, action, table_name, record_id, 
                   old_value, new_value, ip_address)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (user_id, action, table_name, record_id, old_value, new_value, ip_address)
            )
            logger.debug(f"Audit log entry added: {action} on {table_name}")
    except Exception as e:
        logger.error(f"Error adding audit log: {e}")


# ================================================
# SCRUM-92: Validation Functions
# ================================================

def validate_expense_data(expense_date: Any, amount: Any, category: str, 
                         notes: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate expense data before insertion
    Enhancement: SCRUM-92 (Validation)
    
    Returns: (is_valid, error_message)
    """
    # Validate date
    if not expense_date:
        return False, "Expense date is required"
    
    try:
        if isinstance(expense_date, str):
            datetime.strptime(expense_date, '%Y-%m-%d')
        elif not isinstance(expense_date, date):
            return False, "Invalid date format"
    except ValueError:
        return False, "Invalid date format. Expected YYYY-MM-DD"
    
    # Validate amount
    if amount is None:
        return False, "Amount is required"
    
    try:
        amount_decimal = Decimal(str(amount))
        if amount_decimal < 0:
            return False, "Amount cannot be negative"
        if amount_decimal > Decimal('999999.99'):
            return False, "Amount exceeds maximum allowed value"
    except (InvalidOperation, ValueError):
        return False, "Invalid amount format"
    
    # Validate category
    if not category or not category.strip():
        return False, "Category is required"
    
    if len(category) > 100:
        return False, "Category name too long (max 100 characters)"
    
    # Check if category exists
    if not category_exists(category):
        return False, f"Category '{category}' does not exist"
    
    # Validate notes (optional)
    if notes and len(notes) > 5000:
        return False, "Notes too long (max 5000 characters)"
    
    return True, None


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """Validate username"""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 100:
        return False, "Username too long (max 100 characters)"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, None


# ================================================
# SCRUM-96: Custom Category Management
# ================================================

def get_all_categories(active_only: bool = True) -> List[Dict[str, Any]]:
    """
    Get all categories
    Enhancement: SCRUM-96 (Custom Categories)
    """
    logger.info(f"Fetching categories (active_only={active_only})")
    try:
        with get_db_cursor() as cursor:
            if active_only:
                cursor.execute(
                    "SELECT id, name, description, is_active, created_at FROM categories WHERE is_active = TRUE ORDER BY name"
                )
            else:
                cursor.execute(
                    "SELECT id, name, description, is_active, created_at FROM categories ORDER BY name"
                )
            categories = cursor.fetchall()
            logger.info(f"Retrieved {len(categories)} categories")
            return categories
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return []


def category_exists(category_name: str) -> bool:
    """Check if category exists and is active"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id FROM categories WHERE name = %s AND is_active = TRUE",
                (category_name,)
            )
            return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking category existence: {e}")
        return False


def create_category(name: str, description: Optional[str] = None, 
                   created_by: Optional[int] = None) -> Optional[int]:
    """
    Create a new category
    Enhancement: SCRUM-96 (Custom Categories)
    """
    logger.info(f"Creating new category: {name}")
    
    # Validation
    if not name or len(name) < 2:
        logger.error("Category name is required (min 2 characters)")
        return None
    
    if len(name) > 100:
        logger.error("Category name too long")
        return None
    
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """INSERT INTO categories (name, description, created_by, is_active)
                   VALUES (%s, %s, %s, TRUE)""",
                (name, description, created_by)
            )
            category_id = cursor.lastrowid
            logger.info(f"Category created successfully with ID: {category_id}")
            
            # Add audit log
            add_audit_log(created_by, 'CREATE', 'categories', category_id, None, name)
            return category_id
    except mysql.connector.IntegrityError:
        logger.error(f"Category '{name}' already exists")
        return None
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        return None


def update_category(category_id: int, name: Optional[str] = None, 
                   description: Optional[str] = None, user_id: Optional[int] = None) -> bool:
    """
    Update category
    Enhancement: SCRUM-96 (Custom Categories)
    """
    logger.info(f"Updating category ID: {category_id}")
    
    if not name and not description:
        logger.error("Nothing to update")
        return False
    
    try:
        with get_db_cursor(commit=True) as cursor:
            # Get old values for audit
            cursor.execute("SELECT name, description FROM categories WHERE id = %s", (category_id,))
            old_data = cursor.fetchone()
            
            if not old_data:
                logger.error(f"Category {category_id} not found")
                return False
            
            # Build update query dynamically
            updates = []
            params = []
            
            if name:
                updates.append("name = %s")
                params.append(name)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            
            params.append(category_id)
            
            query = f"UPDATE categories SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            
            logger.info(f"Category {category_id} updated successfully")
            
            # Add audit log
            add_audit_log(user_id, 'UPDATE', 'categories', category_id, 
                         str(old_data), f"name={name}, desc={description}")
            return True
    except Exception as e:
        logger.error(f"Error updating category: {e}")
        return False


def delete_category(category_id: int, user_id: Optional[int] = None) -> bool:
    """
    Soft delete category (set is_active = FALSE)
    Enhancement: SCRUM-96 (Custom Categories)
    """
    logger.info(f"Deleting (soft) category ID: {category_id}")
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check if category is in use
            cursor.execute(
                "SELECT COUNT(*) as count FROM expenses WHERE category = (SELECT name FROM categories WHERE id = %s)",
                (category_id,)
            )
            result = cursor.fetchone()
            
            if result and result['count'] > 0:
                logger.warning(f"Category {category_id} is in use by {result['count']} expenses")
                # Still allow soft delete, but log it
            
            cursor.execute(
                "UPDATE categories SET is_active = FALSE WHERE id = %s",
                (category_id,)
            )
            
            if cursor.rowcount > 0:
                logger.info(f"Category {category_id} soft deleted")
                add_audit_log(user_id, 'DELETE', 'categories', category_id, None, None)
                return True
            return False
    except Exception as e:
        logger.error(f"Error deleting category: {e}")
        return False


# ================================================
# SCRUM-93: Filtering and Pagination
# ================================================

def get_filtered_expenses(user_id: int, filters: Optional[Dict[str, Any]] = None, 
                         pagination: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
    """
    Get filtered expenses with pagination
    Enhancement: SCRUM-93 (Filtering)
    
    filters: {
        'start_date': date,
        'end_date': date,
        'category': str,
        'status': str,
        'min_amount': float,
        'max_amount': float
    }
    
    pagination: {
        'limit': int (default 50),
        'offset': int (default 0)
    }
    """
    logger.info(f"Fetching filtered expenses for user {user_id}")
    
    filters = filters or {}
    pagination = pagination or {'limit': 50, 'offset': 0}
    
    try:
        with get_db_cursor() as cursor:
            # Build dynamic query
            query = "SELECT * FROM expenses WHERE user_id = %s"
            params = [user_id]
            
            # Apply filters
            if filters.get('start_date'):
                query += " AND expense_date >= %s"
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                query += " AND expense_date <= %s"
                params.append(filters['end_date'])
            
            if filters.get('category'):
                query += " AND category = %s"
                params.append(filters['category'])
            
            if filters.get('status'):
                query += " AND status = %s"
                params.append(filters['status'])
            
            if filters.get('min_amount') is not None:
                query += " AND amount >= %s"
                params.append(filters['min_amount'])
            
            if filters.get('max_amount') is not None:
                query += " AND amount <= %s"
                params.append(filters['max_amount'])
            
            # Add sorting and pagination
            query += " ORDER BY expense_date DESC, id DESC LIMIT %s OFFSET %s"
            params.extend([pagination['limit'], pagination['offset']])
            
            cursor.execute(query, params)
            expenses = cursor.fetchall()
            
            logger.info(f"Retrieved {len(expenses)} filtered expenses")
            return expenses
    except Exception as e:
        logger.error(f"Error fetching filtered expenses: {e}")
        return []


def get_expense_count(user_id: int, filters: Optional[Dict[str, Any]] = None) -> int:
    """
    Get total count of filtered expenses (for pagination)
    Enhancement: SCRUM-93 (Filtering)
    """
    filters = filters or {}
    try:
        with get_db_cursor() as cursor:
            query = "SELECT COUNT(*) as count FROM expenses WHERE user_id = %s"
            params = [user_id]
            
            # Apply same filters as get_filtered_expenses
            if filters.get('start_date'):
                query += " AND expense_date >= %s"
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                query += " AND expense_date <= %s"
                params.append(filters['end_date'])
            
            if filters.get('category'):
                query += " AND category = %s"
                params.append(filters['category'])
            
            if filters.get('status'):
                query += " AND status = %s"
                params.append(filters['status'])
            
            if filters.get('min_amount') is not None:
                query += " AND amount >= %s"
                params.append(filters['min_amount'])
            
            if filters.get('max_amount') is not None:
                query += " AND amount <= %s"
                params.append(filters['max_amount'])
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] if result else 0
    except Exception as e:
        logger.error(f"Error getting expense count: {e}")
        return 0


# ================================================
# Enhanced Expense Operations
# ================================================

def fetch_expenses_for_date(expense_date: date, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Fetch expenses for a specific date (enhanced with user filter)
    Enhancement: SCRUM-95 (Security), SCRUM-97 (Performance)
    """
    logger.info(f"fetch_expenses_for_date called with expense_date: {expense_date}, user_id: {user_id}")
    try:
        with get_db_cursor() as cursor:
            if user_id:
                cursor.execute(
                    "SELECT * FROM expenses WHERE expense_date = %s AND user_id = %s ORDER BY id",
                    (expense_date, user_id)
                )
            else:
                cursor.execute(
                    "SELECT * FROM expenses WHERE expense_date = %s ORDER BY id",
                    (expense_date,)
                )
            expenses = cursor.fetchall()
            logger.info(f"Retrieved {len(expenses)} expenses")
            return expenses
    except Exception as e:
        logger.error(f"Error fetching expenses: {e}")
        return []


def delete_expenses_for_date(expense_date: date, user_id: int):
    """
    Delete expenses for a specific date (enhanced with security)
    Enhancement: SCRUM-95 (Security)
    """
    logger.info(f"delete_expenses_for_date called with expense_date: {expense_date}, user_id: {user_id}")
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "DELETE FROM expenses WHERE expense_date = %s AND user_id = %s",
                (expense_date, user_id)
            )
            deleted_count = cursor.rowcount
            logger.info(f"Deleted {deleted_count} expenses")
            
            # Add audit log
            add_audit_log(user_id, 'DELETE', 'expenses', None, f"date={expense_date}", None)
    except Exception as e:
        logger.error(f"Error deleting expenses: {e}")
        raise


def insert_expense(expense_date: date, amount: float, category: str, 
                  notes: Optional[str], user_id: int, status: str = 'approved',
                  receipt_path: Optional[str] = None) -> Optional[int]:
    """
    Insert expense with validation
    Enhancement: SCRUM-92 (Validation), SCRUM-95 (Security)
    """
    logger.info(f"insert_expense called with expense_date: {expense_date}, amount: {amount}, "
                f"category: {category}, user_id: {user_id}")
    
    # Validate data
    is_valid, error_msg = validate_expense_data(expense_date, amount, category, notes)
    if not is_valid:
        logger.error(f"Validation failed: {error_msg}")
        raise ValueError(error_msg)
    
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """INSERT INTO expenses (user_id, expense_date, amount, category, notes, status, receipt_path)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (user_id, expense_date, amount, category, notes, status, receipt_path)
            )
            expense_id = cursor.lastrowid
            logger.info(f"Expense inserted successfully with ID: {expense_id}")
            
            # Add audit log
            add_audit_log(user_id, 'INSERT', 'expenses', expense_id, None,
                         f"date={expense_date},amount={amount},category={category}")
            return expense_id
    except Exception as e:
        logger.error(f"Error inserting expense: {e}")
        raise


def fetch_expense_summary(start_date: date, end_date: date, 
                         user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Fetch expense summary with optimization
    Enhancement: SCRUM-97 (Performance)
    """
    logger.info(f"fetch_expense_summary called with start_date: {start_date}, "
                f"end_date: {end_date}, user_id: {user_id}")
    try:
        with get_db_cursor() as cursor:
            if user_id:
                # Use stored procedure for better performance
                cursor.callproc('sp_get_expense_summary', [user_id, start_date, end_date])
                # Fetch results from stored procedure
                for result in cursor.stored_results():
                    data = result.fetchall()
                    logger.info(f"Retrieved summary with {len(data)} categories")
                    return data
            else:
                # Fallback to regular query for admin view
                cursor.execute(
                    '''SELECT category, SUM(amount) AS total, COUNT(*) AS count, AVG(amount) AS average
                       FROM expenses
                       WHERE expense_date BETWEEN %s AND %s AND status = 'approved'
                       GROUP BY category
                       ORDER BY total DESC''',
                    (start_date, end_date)
                )
                data = cursor.fetchall()
                logger.info(f"Retrieved summary with {len(data)} categories")
                return data
    except Exception as e:
        logger.error(f"Error fetching expense summary: {e}")
        return []


# ================================================
# SCRUM-94: Export Functionality
# ================================================

def export_expenses_data(user_id: int, start_date: Optional[date] = None,
                        end_date: Optional[date] = None) -> List[Dict[str, Any]]:
    """
    Get expenses data for export (CSV/PDF)
    Enhancement: SCRUM-94 (Export)
    """
    logger.info(f"Exporting expenses for user {user_id}")
    
    filters = {}
    if start_date:
        filters['start_date'] = start_date
    if end_date:
        filters['end_date'] = end_date
    
    # Get all expenses without pagination for export
    pagination = {'limit': 10000, 'offset': 0}
    
    expenses = get_filtered_expenses(user_id, filters, pagination)
    logger.info(f"Prepared {len(expenses)} expenses for export")
    return expenses


# ================================================
# Utility Functions
# ================================================

def get_expense_by_id(expense_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Get single expense by ID"""
    try:
        with get_db_cursor() as cursor:
            if user_id:
                cursor.execute(
                    "SELECT * FROM expenses WHERE id = %s AND user_id = %s",
                    (expense_id, user_id)
                )
            else:
                cursor.execute("SELECT * FROM expenses WHERE id = %s", (expense_id,))
            
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error fetching expense by ID: {e}")
        return None


def update_expense_status(expense_id: int, status: str, user_id: int) -> bool:
    """Update expense status (for approval workflow)"""
    logger.info(f"Updating expense {expense_id} status to {status}")
    
    if status not in ['pending', 'approved', 'rejected']:
        logger.error(f"Invalid status: {status}")
        return False
    
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE expenses SET status = %s WHERE id = %s",
                (status, expense_id)
            )
            
            if cursor.rowcount > 0:
                add_audit_log(user_id, 'UPDATE_STATUS', 'expenses', expense_id, None, status)
                logger.info(f"Expense status updated successfully")
                return True
            return False
    except Exception as e:
        logger.error(f"Error updating expense status: {e}")
        return False


# ================================================
# Testing and Maintenance
# ================================================

if __name__ == "__main__":
    # Test basic operations
    print("Testing enhanced DB helper...")
    
    # Test category retrieval
    categories = get_all_categories()
    print(f"Categories: {categories}")
    
    # Test validation
    is_valid, msg = validate_expense_data("2024-08-01", 100.50, "Food", "Test notes")
    print(f"Validation result: {is_valid}, {msg}")
    
    print("Basic tests completed")
