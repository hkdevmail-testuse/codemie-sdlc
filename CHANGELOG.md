# Changelog

All notable changes to the Personal Expense Tracker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-XX

### Added
- **UPDATE Expense Feature**: Full CRUD support with ability to edit existing expenses
  - PUT endpoint `/update/<expense_id>` for updating expenses
  - GET endpoint `/expense/<expense_id>` for fetching single expense
  - Edit modal in frontend with pre-filled form
  - Photo update support during edit

- **DELETE Expense Feature**: Complete expense removal capability
  - DELETE endpoint `/delete/<expense_id>` with confirmation
  - Frontend confirmation dialog before deletion
  - Automatic analytics refresh after deletion

- **Advanced Filtering & Sorting**: Enhanced expense list management
  - Search functionality across business, description, and category
  - Sort by date, amount, category, or business name
  - Ascending/descending sort order toggle
  - Category filter dropdown
  - Amount range filtering (min/max)
  - Combined filter application

- **Date Range Analytics**: Flexible date-based reporting
  - Custom start and end date selection for analytics
  - Updated `/overview-data` and `/monthly-category-data` endpoints
  - Date range picker in monthly overview page
  - Backward compatibility with existing month filter

- **Export Functionality**: Data portability features
  - CSV export endpoint `/export/csv` with filtering support
  - PDF export endpoint `/export/pdf` with formatted reports
  - Category summary CSV export `/export/category-csv`
  - Export buttons in UI with proper file downloads
  - PDF reports include summary statistics and detailed tables

- **Enhanced Dashboard**: Improved home page with insights
  - Summary cards for key metrics
  - Quick action buttons
  - Recent activity section
  - Multiple chart views
  - Responsive card layout

- **Mobile Responsiveness**: Optimized for all devices
  - Responsive CSS with mobile-first approach
  - Media queries for tablets (< 768px) and mobile (< 480px)
  - Touch-friendly form inputs and buttons
  - Responsive tables with horizontal scroll
  - Stack layout for small screens
  - Optimized font sizes and spacing

- **Modal System**: Overlay-based edit interface
  - Reusable modal component
  - Smooth open/close animations
  - Accessible close button and backdrop
  - Form validation in modal

- **Configuration Management**: Centralized settings
  - `config.py` module with environment-based configurations
  - Support for development, production, and testing environments
  - Environment variable integration
  - Secure secret key management

- **Validation Utilities**: Robust input validation
  - `validation.py` module with comprehensive validators
  - Date validation (format, future dates, historical limits)
  - Amount validation (positive, numeric, range checks)
  - Text field validation (length, required fields, sanitization)
  - ID validation
  - Sort and pagination parameter validation
  - Search query sanitization
  - File extension validation

- **Export Utilities**: Professional report generation
  - `export_utils.py` module for CSV and PDF generation
  - PDF reports with ReportLab library
  - Formatted tables with alternating row colors
  - Summary statistics in PDF
  - Category-wise summary exports

- **Testing Infrastructure**: Quality assurance setup
  - pytest integration
  - Sample test file for validation utilities
  - Test coverage reporting with pytest-cov
  - Testing configuration in config.py

- **Documentation**: Comprehensive project documentation
  - Enhanced README with full feature list
  - API endpoint documentation
  - Setup and usage instructions
  - Troubleshooting guide
  - .env.example for configuration template
  - CHANGELOG for version tracking

- **Development Tools**: Improved developer experience
  - .gitignore for clean repository
  - Environment variable support with python-dotenv
  - Logging configuration
  - Structured project layout

### Changed
- **Database Schema**: Updated with better indexing
  - Maintained backward compatibility
  - Optimized queries for filtering and sorting

- **Frontend Structure**: Reorganized for maintainability
  - Separated concerns (edit, delete, filter functions)
  - Modular JavaScript functions
  - Consistent error handling
  - Loading state indicators

- **Styling**: Enhanced UI/UX
  - Modern button styles with states (hover, active, disabled)
  - Improved color scheme and contrast
  - Better spacing and typography
  - Consistent form styling
  - Status message styling (success, error, info)

- **API Responses**: Standardized error handling
  - Consistent JSON response format
  - Proper HTTP status codes
  - Detailed error messages
  - Validation error reporting

### Fixed
- Improved error handling for database operations
- Fixed date parsing edge cases
- Enhanced photo upload handling
- Corrected analytics calculation edge cases
- Fixed responsive layout issues on small screens

### Security
- Added input sanitization to prevent XSS
- Implemented proper validation for all user inputs
- Secure file upload handling
- SQL injection prevention (existing, maintained)
- Environment variable protection for secrets

### Dependencies
- Added `reportlab==4.0.7` for PDF generation
- Added `python-dateutil==2.8.2` for date handling
- Added `python-dotenv==1.0.0` for environment management
- Added `pytest==7.4.3` for testing
- Added `pytest-cov==4.1.0` for test coverage
- Kept `Flask==3.0.3` (existing)

---

## [1.0.0] - 2024-XX-XX

### Added
- Initial release with core functionality
- Add expense with date, business, amount, category, description, and photo
- View recent purchases
- Monthly overview with category-wise pie charts
- All-time analytics with line chart
- Photo upload and display support
- Basic field validation
- Chart.js integration for visualizations
- SQLite database with indexed schema
- Flask backend with REST API endpoints
- Responsive HTML5/CSS3 frontend
- Jinja2 templating

### Features
- Expense entry form with validation
- Recent purchases table view
- Monthly spending visualization
- Category-wise expense breakdown
- Photo receipt storage (BLOB)
- JSON API responses
- Mobile-friendly base layout

---

## Version Numbering

- **Major version** (X.0.0): Breaking changes or significant new features
- **Minor version** (1.X.0): New features, backward-compatible
- **Patch version** (1.0.X): Bug fixes and minor improvements
