"""
Configuration module for Personal Expense Tracker.

This module contains all configuration settings for the application.
"""

import os
from pathlib import Path


class Config:
    """Base configuration class."""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    BASE_DIR = Path(__file__).parent
    DATABASE = os.environ.get('EXPENSE_TRACKER_DB') or str(BASE_DIR / 'budget.db')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 6 * 1024 * 1024  # 6MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # Pagination settings
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 500
    
    # Export settings
    EXPORT_MAX_RECORDS = 10000
    PDF_PAGE_SIZE = 'letter'
    
    # Date format settings
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    DISPLAY_DATE_FORMAT = '%B %d, %Y'
    
    # Currency settings
    CURRENCY_SYMBOL = '$'
    CURRENCY_CODE = 'USD'
    
    # Default categories
    DEFAULT_CATEGORIES = [
        'Groceries',
        'Furniture/Home',
        'Gas/Car',
        'Clothes',
        'School/Office Supplies',
        'Restaurants',
        'Misc',
        'Other'
    ]
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    TESTING = False
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'expense_tracker.log')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Override with production database path
    DATABASE = os.environ.get('EXPENSE_TRACKER_DB') or '/var/data/expense_tracker.db'
    
    # Use environment secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    DATABASE = ':memory:'  # Use in-memory database for tests
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Get configuration object based on environment.
    
    Args:
        config_name: Name of configuration ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable or 'default'
    
    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, DevelopmentConfig)
