# Personal Expense Tracker - Enhanced Edition

## Project Overview
Personal Expense Tracker is an enhanced Flask-based web application designed to help users track expenses, manage budgets, analyze spending trends, and make informed financial decisions. The application now includes custom category management, budget cap alerts, CSV import/export, enhanced analytics filters, and improved usability features.

## ✨ New Features & Enhancements

### 1. **Custom Category Management**
- Create, edit, and delete your own expense categories
- Categories are user-specific and available in autocomplete
- Prevents deletion of categories currently in use
- Default categories provided: Groceries, Furniture/Home, Gas/Car, Clothes, School/Office Supplies, Restaurants, Misc

### 2. **Budget Cap Notifications**
- Set monthly budget limits for each category
- Real-time budget status dashboard with visual progress bars
- Automatic alerts when spending exceeds budget
- Color-coded warnings (green, orange, red) based on spending percentage

### 3. **CSV Import/Export**
- Export all expenses to CSV for backup or external analysis
- Import expenses from CSV files with validation
- Duplicate detection prevents redundant entries
- Detailed import summary with error reporting

### 4. **Enhanced Analytics Filters**
- Filter expenses by month, category, tags, or recurring status
- Advanced search capabilities for better expense tracking
- Real-time filtering with instant results

### 5. **Improved Expense Entry Usability**
- Category autocomplete for faster data entry
- Support for tags (comma-separated)
- Recurring expense flag for subscription tracking
- Additional notes field for detailed information
- Enhanced validation with descriptive error messages

### 6. **Security & Privacy**
- Session-based authentication
- User-specific data isolation (multi-user ready)
- Logout functionality to clear session
- Secure database queries with parameterization

## Technology Stack
- **Backend:** Python 3.x, Flask 3.0.3
- **Database:** SQLite (file-based, enhanced schema)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Charts:** Chart.js (CDN)
- **Features:** CSV export/import, autocomplete, budget tracking, filtering

## Database Schema

### Tables
1. **purchases** - Enhanced with tags, recurring flag, notes, user_id
2. **custom_categories** - User-defined expense categories
3. **budgets** - Budget caps per category with period tracking
4. **user_sessions** - Session management for authentication

## Prerequisites
- Python 3.x
- pip

## Installation and Setup

```bash
# Clone the repository
git clone <repository-url>
cd personal-expense-tracker

# Navigate to source directory
cd src

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Build and Run Instructions

### Initialize Database
```bash
cd src
python db/init_db.py
```

### Run the Application
```bash
cd src
python app.py
```

### Access the Application
Open your browser and navigate to: **http://127.0.0.1:5000**

## Project Structure
```text
.
├── README.md
├── docs/
│   └── codemie/...
└── src/
    ├── app.py                    # Enhanced Flask application with new APIs
    ├── requirements.txt          # Python dependencies
    ├── db/
    │   ├── init_db.py           # Database initialization
    │   └── schema.sql           # Enhanced schema with new tables
    ├── static/
    │   ├── script.js            # Main JavaScript with budget alerts
    │   ├── add-expense.js       # Autocomplete functionality
    │   ├── categories.js        # Category management
    │   ├── budgets.js           # Budget management
    │   ├── recent.js            # Enhanced filtering
    │   ├── import-export.js     # CSV functionality
    │   └── styles.css           # Enhanced styling
    └── templates/
        ├── index.html           # Home page with export/import
        ├── add.html             # Add expense with autocomplete
        ├── categories.html      # Manage categories
        ├── budgets.html         # Manage budgets
        ├── recent.html          # View with filters
        └── monthly.html         # Monthly overview
```

## Configuration
Environment variables (optional):
- `EXPENSE_TRACKER_DB` - Path to SQLite DB file (default: `budget.db`)
- `PORT` - Server port (default: `5000`)
- `SECRET_KEY` - Flask secret key for sessions (default: dev key - CHANGE IN PRODUCTION)

## Usage Guide

### 1. Adding Expenses
1. Navigate to **Add Purchase**
2. Fill in required fields (Date, Business, Amount, Category)
3. Use autocomplete for categories (start typing)
4. Add optional tags (comma-separated): e.g., "work, travel, client"
5. Check "Recurring Expense" for subscriptions
6. Add receipt photo if needed
7. Submit - you'll see budget alerts if any category is exceeded

### 2. Managing Categories
1. Navigate to **Manage Categories**
2. View all existing categories
3. Add new categories using the form
4. Edit or delete categories (can't delete if in use)

### 3. Setting Budgets
1. Navigate to **Manage Budgets**
2. View current month budget status with progress bars
3. Add new budgets by selecting category and amount
4. Edit or delete existing budgets
5. Budget status updates automatically

### 4. Viewing & Filtering Expenses
1. Navigate to **View Recent**
2. Use filters to narrow down results:
   - By month (YYYY-MM)
   - By category
   - By tag
   - By recurring status
3. Click **Apply Filters** to see results
4. Click **Clear Filters** to reset

### 5. Exporting Data
1. From the home page, click **Export to CSV**
2. File downloads automatically with all your expenses
3. Open in Excel, Google Sheets, or any CSV viewer

### 6. Importing Data
1. Prepare CSV file with headers: `date, business, amount, category, description, tags, is_recurring, notes`
2. From home page, click **Import from CSV**
3. Select your CSV file
4. View import summary (imported, skipped, errors)
5. Duplicates are automatically detected and skipped

### 7. Analytics
1. **Home Page** - View all-time category breakdown and monthly trends
2. **Monthly Overview** - See spending by month with category breakdowns
3. Charts update based on your data

## CSV Format
```csv
date,business,amount,category,description,tags,is_recurring,notes
2024-01-15,Walmart,125.50,Groceries,Weekly shopping,food,No,Bought organic
2024-01-20,Netflix,15.99,Misc,Streaming,entertainment,Yes,Monthly subscription
```

## API Endpoints

### Expense Management
- `POST /add` - Add new expense
- `GET /month-data` - Get expenses with filters (month, category, tag, recurring)
- `GET /overview-data` - Monthly spending totals
- `GET /monthly-category-data` - Category breakdown

### Category Management
- `GET /api/categories` - List all active categories
- `POST /api/categories` - Create new category
- `PUT /api/categories/<id>` - Update category
- `DELETE /api/categories/<id>` - Delete category (soft delete)

### Budget Management
- `GET /api/budgets` - List all budgets
- `POST /api/budgets` - Create new budget
- `PUT /api/budgets/<id>` - Update budget
- `DELETE /api/budgets/<id>` - Delete budget
- `GET /api/budget-status` - Get current month budget status

### Import/Export
- `GET /api/export-csv` - Export all expenses to CSV
- `POST /api/import-csv` - Import expenses from CSV

### Authentication
- `GET /logout` - Clear session

## Security Considerations

### Current Implementation
- Session-based authentication (auto-login as 'default_user')
- SQL injection protection via parameterized queries
- File upload size limits (6MB)
- CSV validation and duplicate detection
- Soft deletes for data integrity

### Production Recommendations
1. **Change SECRET_KEY** - Set a strong, random secret key
2. **Add Authentication** - Implement proper user registration/login
3. **Use HTTPS** - Enable SSL/TLS for encrypted communication
4. **Rate Limiting** - Prevent abuse of API endpoints
5. **Input Sanitization** - Additional validation layers
6. **Database Backups** - Regular automated backups
7. **Error Logging** - Implement comprehensive logging

## Code Quality & Best Practices

### Implemented
✅ Modular code structure  
✅ RESTful API design  
✅ Parameterized SQL queries  
✅ Error handling and validation  
✅ Responsive design  
✅ Clean separation of concerns  
✅ Idempotent database migrations  
✅ User feedback messages  
✅ Progress indicators  

### Testing Recommendations
- Unit tests for API endpoints
- Integration tests for database operations
- UI tests for form validation
- Load testing for CSV import with large files

## Known Limitations
1. **Single User Mode** - While multi-user ready, authentication is simplified
2. **No Password Protection** - Sessions auto-assign default user
3. **Photo Storage** - Photos stored as BLOBs (consider external storage for scale)
4. **CSV Size** - Large imports may timeout (consider chunking)
5. **Browser Storage** - Sessions stored server-side only

## Future Enhancements
- [ ] User registration and authentication
- [ ] Email notifications for budget alerts
- [ ] Recurring expense automation
- [ ] Mobile app (React Native / Flutter)
- [ ] Bank integration / API imports
- [ ] Advanced reporting (PDF export)
- [ ] Multi-currency support
- [ ] Expense sharing / splitting
- [ ] AI-powered category suggestions
- [ ] Budget forecasting / predictions

## Troubleshooting

### Database Issues
```bash
# Reset database
rm budget.db
python db/init_db.py
```

### Port Already in Use
```bash
# Change port
export PORT=8080  # macOS/Linux
set PORT=8080     # Windows
python app.py
```

### Module Not Found
```bash
pip install -r requirements.txt
```

## Documentation
Comprehensive documentation available on Confluence:
- [Documentation Hub](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/18513929/Personal+Expense+Tracker+-+Documentation)
- [FRD](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/19038209/FRD+-+Personal+Expense+Tracker)
- [Architecture](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/19070977/Architecture+-+Personal+Expense+Tracker)
- [Design (HLD & LLD)](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/19103745/Design+HLD+LLD+-+Personal+Expense+Tracker)
- [Wireframes](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/18219028/Wireframes+-+Personal+Expense+Tracker)

## Version Control
- **Repository:** github_test_task
- **Branch:** dev_branch
- **Latest Features:** Custom categories, budget caps, CSV import/export, enhanced filters

## Contributing
1. Create feature branch from `dev_branch`
2. Implement changes with tests
3. Submit pull request with description
4. Code review and approval required

## Support
For issues or questions:
1. Check documentation
2. Review troubleshooting section
3. Check existing issues in repository
4. Create new issue with details

## License
Internal EPAM project - All rights reserved

## Changelog

### v2.0.0 - Enhanced Edition (2024)
- ✨ Added custom category management
- ✨ Added budget cap tracking with alerts
- ✨ Added CSV import/export functionality
- ✨ Enhanced analytics with multiple filters
- ✨ Improved expense entry with autocomplete
- ✨ Added tags and recurring expense support
- ✨ Implemented session-based authentication
- 🎨 Enhanced UI with budget status cards
- 🐛 Fixed validation and error handling
- 📝 Comprehensive documentation

### v1.0.0 - Initial Release
- Basic expense tracking
- Monthly overview with charts
- Category-based analytics
- Receipt photo upload
- Chart.js visualizations

---

**Built with ❤️ for better personal finance management**
