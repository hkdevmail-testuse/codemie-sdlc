"""
Unit tests for validation utilities.

Run with: python -m pytest tests/test_validation.py
"""

import pytest
from datetime import datetime
from utils.validation import (
    validate_date,
    validate_amount,
    validate_text_field,
    validate_category,
    validate_id,
    validate_sort_params,
    validate_pagination,
    validate_search_query,
    sanitize_filename,
    validate_file_extension
)


class TestDateValidation:
    """Tests for date validation."""
    
    def test_valid_date(self):
        """Test validation of valid date string."""
        is_valid, error, parsed = validate_date('2024-01-15')
        assert is_valid is True
        assert error is None
        assert isinstance(parsed, datetime)
    
    def test_invalid_date_format(self):
        """Test validation of invalid date format."""
        is_valid, error, parsed = validate_date('15/01/2024')
        assert is_valid is False
        assert error is not None
        assert parsed is None
    
    def test_future_date(self):
        """Test validation of future date."""
        is_valid, error, parsed = validate_date('2099-12-31')
        assert is_valid is False
        assert 'future' in error.lower()
    
    def test_empty_date(self):
        """Test validation of empty date."""
        is_valid, error, parsed = validate_date('')
        assert is_valid is False
        assert error is not None


class TestAmountValidation:
    """Tests for amount validation."""
    
    def test_valid_amount(self):
        """Test validation of valid amount."""
        is_valid, error, amount = validate_amount(100.50)
        assert is_valid is True
        assert error is None
        assert amount == 100.50
    
    def test_negative_amount(self):
        """Test validation of negative amount."""
        is_valid, error, amount = validate_amount(-50)
        assert is_valid is False
        assert 'negative' in error.lower()
    
    def test_zero_amount(self):
        """Test validation of zero amount."""
        is_valid, error, amount = validate_amount(0)
        assert is_valid is False
        assert 'greater than zero' in error.lower()
    
    def test_string_amount(self):
        """Test validation of string amount."""
        is_valid, error, amount = validate_amount('123.45')
        assert is_valid is True
        assert amount == 123.45
    
    def test_invalid_amount_format(self):
        """Test validation of invalid amount format."""
        is_valid, error, amount = validate_amount('abc')
        assert is_valid is False
        assert 'invalid' in error.lower()


class TestTextFieldValidation:
    """Tests for text field validation."""
    
    def test_valid_text(self):
        """Test validation of valid text."""
        is_valid, error, text = validate_text_field('Test Business', 'Business')
        assert is_valid is True
        assert error is None
        assert text == 'Test Business'
    
    def test_empty_required_field(self):
        """Test validation of empty required field."""
        is_valid, error, text = validate_text_field('', 'Business', required=True)
        assert is_valid is False
        assert 'required' in error.lower()
    
    def test_empty_optional_field(self):
        """Test validation of empty optional field."""
        is_valid, error, text = validate_text_field('', 'Description', required=False)
        assert is_valid is True
        assert text == ''
    
    def test_text_too_long(self):
        """Test validation of text exceeding max length."""
        long_text = 'a' * 300
        is_valid, error, text = validate_text_field(long_text, 'Business', max_length=255)
        assert is_valid is False
        assert 'too long' in error.lower()
    
    def test_text_with_whitespace(self):
        """Test that whitespace is trimmed."""
        is_valid, error, text = validate_text_field('  Test  ', 'Business')
        assert is_valid is True
        assert text == 'Test'


class TestCategoryValidation:
    """Tests for category validation."""
    
    def test_valid_category(self):
        """Test validation of valid category."""
        is_valid, error, cat = validate_category('Groceries')
        assert is_valid is True
        assert cat == 'Groceries'
    
    def test_category_with_allowed_list(self):
        """Test validation with allowed categories list."""
        allowed = ['Groceries', 'Gas/Car', 'Restaurants']
        is_valid, error, cat = validate_category('Groceries', allowed)
        assert is_valid is True
    
    def test_invalid_category_from_list(self):
        """Test validation of category not in allowed list."""
        allowed = ['Groceries', 'Gas/Car']
        is_valid, error, cat = validate_category('Other', allowed)
        assert is_valid is False


class TestIdValidation:
    """Tests for ID validation."""
    
    def test_valid_id(self):
        """Test validation of valid ID."""
        is_valid, error, id_val = validate_id(123)
        assert is_valid is True
        assert id_val == 123
    
    def test_string_id(self):
        """Test validation of string ID."""
        is_valid, error, id_val = validate_id('456')
        assert is_valid is True
        assert id_val == 456
    
    def test_negative_id(self):
        """Test validation of negative ID."""
        is_valid, error, id_val = validate_id(-1)
        assert is_valid is False
    
    def test_zero_id(self):
        """Test validation of zero ID."""
        is_valid, error, id_val = validate_id(0)
        assert is_valid is False


class TestSortParamsValidation:
    """Tests for sort parameters validation."""
    
    def test_valid_sort_params(self):
        """Test validation of valid sort parameters."""
        is_valid, error, (sort_by, sort_order) = validate_sort_params('amount', 'desc')
        assert is_valid is True
        assert sort_by == 'amount'
        assert sort_order == 'DESC'
    
    def test_default_sort_params(self):
        """Test default sort parameters."""
        is_valid, error, (sort_by, sort_order) = validate_sort_params(None, None)
        assert is_valid is True
        assert sort_by == 'date'
        assert sort_order == 'DESC'
    
    def test_invalid_sort_field(self):
        """Test validation of invalid sort field."""
        is_valid, error, params = validate_sort_params('invalid_field', 'asc')
        assert is_valid is False


class TestPaginationValidation:
    """Tests for pagination validation."""
    
    def test_valid_pagination(self):
        """Test validation of valid pagination parameters."""
        is_valid, error, (limit, offset) = validate_pagination(20, 10)
        assert is_valid is True
        assert limit == 20
        assert offset == 10
    
    def test_default_pagination(self):
        """Test default pagination parameters."""
        is_valid, error, (limit, offset) = validate_pagination(None, None)
        assert is_valid is True
        assert limit == 50
        assert offset == 0
    
    def test_limit_too_high(self):
        """Test validation of limit exceeding maximum."""
        is_valid, error, params = validate_pagination(1000, 0)
        assert is_valid is False


class TestSearchQueryValidation:
    """Tests for search query validation."""
    
    def test_valid_search(self):
        """Test validation of valid search query."""
        is_valid, error, search = validate_search_query('grocery store')
        assert is_valid is True
        assert search == 'grocery store'
    
    def test_empty_search(self):
        """Test validation of empty search query."""
        is_valid, error, search = validate_search_query('')
        assert is_valid is True
        assert search is None
    
    def test_none_search(self):
        """Test validation of None search query."""
        is_valid, error, search = validate_search_query(None)
        assert is_valid is True
        assert search is None


class TestFilenameValidation:
    """Tests for filename sanitization and validation."""
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        result = sanitize_filename('test file!@#.pdf')
        assert '!' not in result
        assert '@' not in result
    
    def test_sanitize_path_in_filename(self):
        """Test that path separators are removed."""
        result = sanitize_filename('../../../etc/passwd')
        assert '/' not in result
        assert '\\' not in result
    
    def test_valid_file_extension(self):
        """Test validation of valid file extension."""
        allowed = {'pdf', 'csv', 'xlsx'}
        is_valid, error = validate_file_extension('report.pdf', allowed)
        assert is_valid is True
    
    def test_invalid_file_extension(self):
        """Test validation of invalid file extension."""
        allowed = {'pdf', 'csv'}
        is_valid, error = validate_file_extension('file.exe', allowed)
        assert is_valid is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
