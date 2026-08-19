"""
Validation utilities for Personal Expense Tracker.

This module provides input validation and sanitization functions.
"""

from datetime import datetime
from typing import Tuple, Optional, Any
import re


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_date(date_str: str, date_format: str = '%Y-%m-%d') -> Tuple[bool, Optional[str], Optional[datetime]]:
    """
    Validate date string.
    
    Args:
        date_str: Date string to validate
        date_format: Expected date format
        
    Returns:
        Tuple of (is_valid, error_message, parsed_date)
    """
    if not date_str or not isinstance(date_str, str):
        return False, "Date is required", None
    
    date_str = date_str.strip()
    
    try:
        parsed_date = datetime.strptime(date_str, date_format)
        
        # Check if date is not in the future
        if parsed_date > datetime.now():
            return False, "Date cannot be in the future", None
        
        # Check if date is not too old (e.g., before year 1900)
        if parsed_date.year < 1900:
            return False, "Date is too old", None
        
        return True, None, parsed_date
    except ValueError:
        return False, f"Invalid date format. Expected {date_format}", None


def validate_amount(amount: Any) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Validate expense amount.
    
    Args:
        amount: Amount to validate (can be string, int, or float)
        
    Returns:
        Tuple of (is_valid, error_message, parsed_amount)
    """
    if amount is None or str(amount).strip() == '':
        return False, "Amount is required", None
    
    try:
        amount_float = float(amount)
        
        if amount_float < 0:
            return False, "Amount cannot be negative", None
        
        if amount_float == 0:
            return False, "Amount must be greater than zero", None
        
        if amount_float > 1000000000:  # 1 billion limit
            return False, "Amount is too large", None
        
        # Round to 2 decimal places
        amount_float = round(amount_float, 2)
        
        return True, None, amount_float
    except (ValueError, TypeError):
        return False, "Invalid amount format. Must be a number", None


def validate_text_field(text: str, field_name: str, 
                       min_length: int = 1, 
                       max_length: int = 255,
                       required: bool = True) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate text field.
    
    Args:
        text: Text to validate
        field_name: Name of the field (for error messages)
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        required: Whether the field is required
        
    Returns:
        Tuple of (is_valid, error_message, cleaned_text)
    """
    if text is None:
        text = ''
    
    if not isinstance(text, str):
        text = str(text)
    
    text = text.strip()
    
    if required and len(text) < min_length:
        return False, f"{field_name} is required", None
    
    if not required and len(text) == 0:
        return True, None, text
    
    if len(text) > max_length:
        return False, f"{field_name} is too long (max {max_length} characters)", None
    
    # Basic sanitization - remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    return True, None, text


def validate_category(category: str, allowed_categories: list = None) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate expense category.
    
    Args:
        category: Category to validate
        allowed_categories: List of allowed categories (None = any non-empty string)
        
    Returns:
        Tuple of (is_valid, error_message, cleaned_category)
    """
    is_valid, error, cleaned = validate_text_field(category, "Category", min_length=1, max_length=100)
    
    if not is_valid:
        return is_valid, error, cleaned
    
    if allowed_categories and cleaned not in allowed_categories:
        return False, f"Invalid category. Must be one of: {', '.join(allowed_categories)}", None
    
    return True, None, cleaned


def validate_id(id_value: Any) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Validate ID value.
    
    Args:
        id_value: ID to validate
        
    Returns:
        Tuple of (is_valid, error_message, parsed_id)
    """
    try:
        id_int = int(id_value)
        
        if id_int < 1:
            return False, "ID must be a positive integer", None
        
        return True, None, id_int
    except (ValueError, TypeError):
        return False, "Invalid ID format", None


def validate_sort_params(sort_by: Optional[str], sort_order: Optional[str]) -> Tuple[bool, Optional[str], Tuple[str, str]]:
    """
    Validate sorting parameters.
    
    Args:
        sort_by: Field to sort by
        sort_order: Sort order ('asc' or 'desc')
        
    Returns:
        Tuple of (is_valid, error_message, (sort_by, sort_order))
    """
    allowed_sort_fields = ['date', 'amount', 'category', 'business', 'created_at']
    allowed_sort_orders = ['asc', 'desc']
    
    # Default values
    if not sort_by:
        sort_by = 'date'
    if not sort_order:
        sort_order = 'desc'
    
    sort_by = sort_by.lower().strip()
    sort_order = sort_order.lower().strip()
    
    if sort_by not in allowed_sort_fields:
        return False, f"Invalid sort field. Must be one of: {', '.join(allowed_sort_fields)}", (sort_by, sort_order)
    
    if sort_order not in allowed_sort_orders:
        return False, f"Invalid sort order. Must be 'asc' or 'desc'", (sort_by, sort_order)
    
    return True, None, (sort_by, sort_order.upper())


def validate_pagination(limit: Any, offset: Any = 0) -> Tuple[bool, Optional[str], Tuple[int, int]]:
    """
    Validate pagination parameters.
    
    Args:
        limit: Number of records to return
        offset: Number of records to skip
        
    Returns:
        Tuple of (is_valid, error_message, (limit, offset))
    """
    try:
        limit = int(limit) if limit else 50
        offset = int(offset) if offset else 0
        
        if limit < 1:
            return False, "Limit must be at least 1", (limit, offset)
        
        if limit > 500:
            return False, "Limit cannot exceed 500", (limit, offset)
        
        if offset < 0:
            return False, "Offset cannot be negative", (limit, offset)
        
        return True, None, (limit, offset)
    except (ValueError, TypeError):
        return False, "Invalid pagination parameters", (50, 0)


def validate_search_query(search: Optional[str]) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate and sanitize search query.
    
    Args:
        search: Search query string
        
    Returns:
        Tuple of (is_valid, error_message, cleaned_search)
    """
    if not search:
        return True, None, None
    
    if not isinstance(search, str):
        search = str(search)
    
    search = search.strip()
    
    if len(search) == 0:
        return True, None, None
    
    if len(search) > 255:
        return False, "Search query is too long (max 255 characters)", None
    
    # Basic sanitization
    search = re.sub(r'[^\w\s\-\.]', '', search)
    
    return True, None, search


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "file"
    
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s\-\.]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename


def validate_file_extension(filename: str, allowed_extensions: set) -> Tuple[bool, Optional[str]]:
    """
    Validate file extension.
    
    Args:
        filename: Filename to validate
        allowed_extensions: Set of allowed extensions (without dot)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return True, None  # No file is often optional
    
    if '.' not in filename:
        return False, "File must have an extension"
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if ext not in allowed_extensions:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, None
