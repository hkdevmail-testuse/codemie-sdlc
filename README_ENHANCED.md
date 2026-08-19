# Personal Expense Tracker - Enhanced Version

## Project Overview
Personal Expense Tracker is a Flask-based web application to record, manage, and analyze expenses with powerful visualization and filtering capabilities. This enhanced version includes edit/delete functionality, advanced filtering, date range analytics, and an improved user interface.

## Technology Stack
- **Backend:** Python 3.x, Flask 3.0.3
- **Database:** SQLite (file-based, with schema migration support)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Jinja2 templates
- **Charts:** Chart.js (CDN)
- **Images:** Receipt images stored as BLOBs; served as Base64 strings in JSON responses

## Key Features

### Core Functionality
✅ Add expenses with date, business, amount, category, description, and optional receipt photo
✅ **NEW:** Edit existing expenses with validation
✅ **NEW:** Delete expenses with confirmation dialog
✅ View recent expenses in an interactive table
✅ Monthly and all-time analytics with pie and line charts

### Enhanced Features
🆕 **Advanced Filtering**
- Filter expenses by date range (start date / end date)
- Filter by category
- Search by business name (partial match)
- Filter by amount range (min/max)
- Combine multiple filters for precise results

🆕 **Date Range Analytics**
- Custom date range selection for charts
- Filter monthly spending trends by date
- Filter category-wise spending by date range
- Real-time chart updates based on selected filters

🆕 **Improved UI/UX**
- Modern modal dialogs for editing expenses
- Confirmation dialogs for delete operations
- Responsive design for mobile and tablet devices
- Visual feedback for all operations (success/error messages)
- Hover effects and smooth transitions
- Accessible color schemes and button styles

🆕 **Data Management**
- Audit trail with `updated_at` timestamp
- Schema migration support for existing databases
- RESTful API endpoints for CRUD operations
- Better error handling and validation

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Installation and Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd personal-expense-tracker
```

### 2. Set Up Virtual Environment
```bash
cd src
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
# The database will be automatically initialized on first run
# Or manually initialize:
python db/init_db_v2.py
```

## Running the Application

### Development Mode
```bash
cd src
python app_enhanced.py
```

The application will start on `http://127.0.0.1:5000`

### Production Mode
For production deployment, use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_enhanced:app
```

## Project Structure
```
.
├── README.md
├── README_ENHANCED.md (this file)
├── docs/
│   └── codemie/
│       └── analytics/
└── src/
    ├── app.py                      # Original Flask application
    ├── app_enhanced.py             # Enhanced Flask application with new features
    ├── requirements.txt
    ├── db/
    │   ├── init_db.py             # Original database initialization
    │   ├── init_db_v2.py          # Enhanced with migration support
    │   ├── schema.sql             # Original database schema
    │   └── schema_v2.sql          # Enhanced schema with audit trail
    ├── static/
    │   ├── images/
    │   ├── script.js              # Original JavaScript
    │   ├── script_enhanced.js     # Enhanced with edit/delete/filter features
    │   ├── styles.css             # Original styles
    │   └── styles_enhanced.css    # Enhanced styles with modals and responsive design
    └── templates/
        ├── index.html             # Original home page
        ├── index_enhanced.html    # Enhanced with date range filtering
        ├── add.html               # Original add page
        ├── add_enhanced.html      # Enhanced with better validation
        ├── recent.html            # Original recent page
        ├── recent_enhanced.html   # Enhanced with filters and actions
        ├── monthly.html           # Original monthly page
        └── monthly_enhanced.html  # Enhanced monthly overview
```

## Configuration
Environment variables:
- `EXPENSE_TRACKER_DB` (optional): Path to SQLite database file (default: `budget.db`)
- `PORT` (optional): Server port (default: `5000`)

## API Endpoints

### Expense Management
- `GET /` - Home page with analytics
- `GET /add` - Add expense page
- `GET /recent` - Recent expenses page with filters
- `GET /monthly` - Monthly overview page

### RESTful API
- `POST /add` - Create new expense
- `GET /purchase/<id>` - Get single expense by ID
- `PUT /purchase/<id>` - Update expense (JSON)
- `DELETE /purchase/<id>` - Delete expense

### Data Retrieval
- `GET /month-data` - Get expenses with filtering
  - Query params: `limit`, `month`, `start_date`, `end_date`, `category`, `business`, `min_amount`, `max_amount`
- `GET /overview-data` - Get monthly totals
  - Query params: `sort`, `start_date`, `end_date`
- `GET /monthly-category-data` - Get category-wise spending
  - Query params: `month`, `start_date`, `end_date`
- `GET /categories` - Get list of all categories

## Database Schema

### purchases Table
```sql
CREATE TABLE purchases (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,                  -- ISO-8601 (YYYY-MM-DD)
  business TEXT NOT NULL,
  amount REAL NOT NULL CHECK (amount >= 0),
  category TEXT NOT NULL,
  description TEXT,
  photo BLOB,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Indices for performance
CREATE INDEX idx_purchases_date ON purchases(date);
CREATE INDEX idx_purchases_category ON purchases(category);
CREATE INDEX idx_purchases_business ON purchases(business);
```

## Usage Guide

### Adding an Expense
1. Navigate to "Add Purchase" page
2. Fill in date, business name, amount, and category
3. Optionally add description and receipt photo
4. Click "Add Purchase"
5. See success confirmation

### Editing an Expense
1. Go to "View Recent" page
2. Find the expense you want to edit
3. Click "Edit" button
4. Modify fields in the modal dialog
5. Click "Save Changes"

### Deleting an Expense
1. Go to "View Recent" page
2. Find the expense you want to delete
3. Click "Delete" button
4. Confirm deletion in the dialog
5. Expense is permanently removed

### Filtering Expenses
1. Go to "View Recent" page
2. Use the filter panel at the top
3. Select date range, category, business, or amount range
4. Click "Apply Filters"
5. View filtered results

### Viewing Analytics
1. Go to Home page
2. Use date range filter to customize view
3. View monthly spending trends (line chart)
4. View category-wise breakdown (pie chart)
5. Navigate to "Monthly Overview" for month-by-month details

## Enhancement Summary

### What Was Added
1. **Update/Edit Expense Functionality** ✅
   - Modal-based edit form
   - Field validation
   - Real-time updates

2. **Delete Expense Functionality** ✅
   - Confirmation dialog
   - Immediate removal from UI
   - Database cleanup

3. **Advanced Filtering** ✅
   - Multi-criteria filtering
   - Date range selection
   - Category and business filters
   - Amount range filters

4. **Date Range Analytics** ✅
   - Custom date range for charts
   - Dynamic chart updates
   - Flexible time period selection

5. **UI/UX Improvements** ✅
   - Modal dialogs
   - Responsive design
   - Better feedback messages
   - Improved styling

6. **Database Enhancements** ✅
   - Audit trail (updated_at)
   - Migration support
   - Additional indices

## Testing

### Manual Testing Checklist
- [ ] Add a new expense
- [ ] Edit an existing expense
- [ ] Delete an expense
- [ ] Filter expenses by date range
- [ ] Filter expenses by category
- [ ] Search expenses by business name
- [ ] Filter expenses by amount range
- [ ] View analytics with date range filter
- [ ] Test responsive design on mobile
- [ ] Verify charts update correctly

### Test Data
You can use the following test scenarios:
1. Add expenses across multiple months
2. Create expenses in different categories
3. Test edge cases (very small/large amounts)
4. Test with and without photos
5. Test filter combinations

## Known Limitations
- Single-user application (no authentication)
- File-based SQLite database (not suitable for high concurrency)
- Receipt photos limited to 6MB
- No data export functionality (can be added)
- No recurring expenses support (can be added)

## Future Enhancements (Roadmap)
- [ ] User authentication and multi-user support
- [ ] Export to CSV/PDF
- [ ] Recurring expenses
- [ ] Budget setting and alerts
- [ ] Email notifications
- [ ] Mobile app (React Native/Flutter)
- [ ] Cloud backup
- [ ] Category budgets and spending limits
- [ ] Expense tags/labels
- [ ] Advanced analytics (trends, predictions)

## Migration from Original Version

### For Existing Users
If you're upgrading from the original version:

1. **Backup your database:**
   ```bash
   cp budget.db budget_backup.db
   ```

2. **Update file references in templates:**
   - Replace `styles.css` with `styles_enhanced.css`
   - Replace `script.js` with `script_enhanced.js`

3. **Switch to enhanced app:**
   ```bash
   python app_enhanced.py
   ```

4. **Database migration:**
   The enhanced `init_db_v2.py` automatically adds the `updated_at` column if it doesn't exist.

## Troubleshooting

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
rm budget.db
python db/init_db_v2.py
```

### Port Already in Use
```bash
# Change port
export PORT=8000
python app_enhanced.py
```

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

## Documentation
Additional documentation available on Confluence:
- [Documentation Hub](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/18513929/Personal+Expense+Tracker+-+Documentation)
- [FRD - Functional Requirements](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/19038209/FRD+-+Personal+Expense+Tracker)
- [Architecture Document](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/19070977/Architecture+-+Personal+Expense+Tracker)
- [Design (HLD & LLD)](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/19103745/Design+HLD+LLD+-+Personal+Expense+Tracker)
- [Wireframes](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/18219028/Wireframes+-+Personal+Expense+Tracker)

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## License
This project is for educational and personal use.

## Support
For issues or questions, please create an issue in the repository.

---

## Version History
- **v2.0** (Enhanced Version) - Added edit, delete, advanced filtering, date range analytics, improved UI
- **v1.0** (Original Version) - Basic expense tracking with charts

**Built with ❤️ using Flask and vanilla JavaScript**
