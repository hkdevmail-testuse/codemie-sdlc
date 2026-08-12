# Personal Expense Tracker - Enhanced Edition

## Project Overview
Personal Expense Tracker is an advanced Flask-based web application designed to help users track expenses, manage budgets, analyze spending trends, and make informed financial decisions. The application features comprehensive CRUD operations, custom category management, budget cap alerts, CSV/PDF export capabilities, advanced filtering and sorting, mobile-responsive design, and enhanced analytics with interactive visualizations.

### Key Capabilities
- **Full CRUD Operations**: Create, Read, Update, and Delete expenses with ease
- **Advanced Filtering & Sorting**: Filter by month, category, tags, recurring status with multi-column sorting
- **Export Flexibility**: Export data to CSV or professionally formatted PDF reports
- **Budget Management**: Set monthly budget limits with real-time alerts and visual progress indicators
- **Custom Categories**: Create and manage your own expense categories
- **Mobile Responsive**: Fully optimized for desktop, tablet, and mobile devices
- **Rich Analytics**: Interactive charts and graphs for spending insights

---

## ✨ Features

### 🎯 Core Features
- ✅ **Add Expenses** - Quick expense entry with autocomplete and validation
- ✅ **Edit Expenses** - Modify existing expenses with pre-filled forms
- ✅ **Delete Expenses** - Remove expenses with confirmation dialog
- ✅ **View Recent Expenses** - Paginated list with sorting and filtering
- ✅ **Expense Details** - View complete expense information including photos
- ✅ **Receipt Upload** - Attach receipt photos (up to 6MB)
- ✅ **Tags Support** - Add comma-separated tags for better organization
- ✅ **Recurring Expenses** - Flag subscriptions and recurring payments
- ✅ **Notes Field** - Add detailed notes to each expense

### 📊 Analytics & Insights
- ✅ **Category Breakdown** - Pie chart showing spending by category
- ✅ **Monthly Trends** - Line chart tracking spending over time
- ✅ **Budget Status Dashboard** - Real-time budget monitoring with progress bars
- ✅ **Monthly Overview** - Detailed month-by-month analysis
- ✅ **Category-wise Analysis** - Drill down into specific categories
- ✅ **Spending Summaries** - Total, average, and category totals

### 💰 Budget Management
- ✅ **Budget Caps** - Set monthly limits per category
- ✅ **Budget Alerts** - Automatic warnings when exceeding limits
- ✅ **Visual Indicators** - Color-coded progress bars (green/orange/red)
- ✅ **Budget CRUD** - Create, edit, and delete budget limits
- ✅ **Period Tracking** - Monthly budget reset and tracking

### 🏷️ Category Management
- ✅ **Custom Categories** - Create user-specific categories
- ✅ **Category CRUD** - Full create, read, update, delete operations
- ✅ **Default Categories** - Pre-loaded with common expense types
- ✅ **Usage Protection** - Prevents deletion of categories in use
- ✅ **Autocomplete** - Quick category selection during expense entry

### 📤 Export & Import
- ✅ **CSV Export** - Export all expenses to CSV format
- ✅ **PDF Export** - Generate professionally formatted PDF reports
- ✅ **CSV Import** - Bulk import expenses from CSV files
- ✅ **Duplicate Detection** - Automatic detection of duplicate entries
- ✅ **Validation** - Data validation during import with error reporting
- ✅ **Import Summary** - Detailed report of imported/skipped/error records

### 🔍 Advanced Filtering & Search
- ✅ **Month Filter** - Filter expenses by specific month (YYYY-MM)
- ✅ **Category Filter** - Filter by one or multiple categories
- ✅ **Tag Filter** - Search by tags
- ✅ **Recurring Filter** - Filter recurring vs. one-time expenses
- ✅ **Multi-column Sorting** - Sort by date, amount, category, business
- ✅ **Real-time Filtering** - Instant results as you filter
- ✅ **Clear Filters** - One-click filter reset

### 🎨 UI/UX Enhancements
- ✅ **Responsive Design** - Mobile, tablet, and desktop optimized
- ✅ **Modern Interface** - Clean, intuitive design
- ✅ **Interactive Charts** - Chart.js powered visualizations
- ✅ **Toast Notifications** - Non-intrusive success/error messages
- ✅ **Loading Indicators** - Progress feedback for async operations
- ✅ **Form Validation** - Real-time input validation with helpful messages
- ✅ **Modal Dialogs** - Confirmation dialogs for destructive actions
- ✅ **Autocomplete** - Type-ahead suggestions for categories

### 🔐 Security & Privacy
- ✅ **Session Management** - Secure session-based authentication
- ✅ **User Isolation** - Multi-user ready with data separation
- ✅ **SQL Injection Protection** - Parameterized queries
- ✅ **File Upload Validation** - Size and type restrictions
- ✅ **Soft Deletes** - Data integrity with soft delete for categories
- ✅ **Logout Functionality** - Session clearing on logout

---

## Technology Stack

### Backend
- **Python** 3.x - Core programming language
- **Flask** 3.0.3 - Web framework
- **SQLite** - File-based database (zero configuration)
- **ReportLab** 4.2.5 - PDF generation library
- **python-dateutil** 2.9.0 - Date parsing and manipulation

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with flexbox/grid
- **Vanilla JavaScript** - No framework dependencies
- **Chart.js** (CDN) - Interactive charts and graphs

### Key Libraries
- **Werkzeug** - File upload handling and utilities
- **Jinja2** - Template engine (included with Flask)
- **ReportLab** - Professional PDF report generation
- **python-dateutil** - Enhanced date parsing for CSV import

---

## Prerequisites
- **Python** 3.7 or higher
- **pip** (Python package manager)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd personal-expense-tracker
```

### 2. Navigate to Source Directory
```bash
cd src
```

### 3. Create and Activate Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note:** ReportLab may require minimal system dependencies:
- **Windows**: No additional requirements
- **macOS**: May require `brew install freetype` (usually pre-installed)
- **Linux**: May require `sudo apt-get install libfreetype6-dev` (Debian/Ubuntu)

### 5. Initialize Database
```bash
python db/init_db.py
```

You should see:
```
Database initialized successfully!
Default categories created.
```

---

## Build and Run Instructions

### Run the Application
```bash
cd src
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Access the Application
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Stop the Application
Press `Ctrl + C` in the terminal

---

## Project Structure
```text
personal-expense-tracker/
├── README.md                       # This file
├── docs/                          # Additional documentation
│   └── codemie/                   # Confluence documentation exports
└── src/                           # Application source code
    ├── app.py                     # Flask application with all routes
    ├── requirements.txt           # Python dependencies
    ├── db/                        # Database files
    │   ├── init_db.py            # Database initialization script
    │   ├── schema.sql            # Database schema definition
    │   └── budget.db             # SQLite database (created at runtime)
    ├── static/                    # Static assets (CSS, JS, images)
    │   ├── styles.css            # Main stylesheet
    │   ├── script.js             # Home page logic with charts
    │   ├── add-expense.js        # Add/Edit expense form logic
    │   ├── categories.js         # Category management
    │   ├── budgets.js            # Budget management
    │   ├── recent.js             # Recent expenses with filtering
    │   └── import-export.js      # CSV/PDF export logic
    └── templates/                 # HTML templates (Jinja2)
        ├── index.html            # Home page with dashboard
        ├── add.html              # Add expense form
        ├── edit.html             # Edit expense form
        ├── categories.html       # Category management page
        ├── budgets.html          # Budget management page
        ├── recent.html           # Recent expenses with filters
        └── monthly.html          # Monthly overview page
```

---

## Database Schema

### Tables

#### 1. **purchases** - Main expense records
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
date TEXT NOT NULL                    -- Format: YYYY-MM-DD
business TEXT NOT NULL                -- Business/vendor name
amount REAL NOT NULL                  -- Expense amount
category TEXT NOT NULL                -- Category name
description TEXT                      -- Optional description
photo BLOB                            -- Receipt photo (binary)
tags TEXT                             -- Comma-separated tags
is_recurring TEXT DEFAULT 'No'       -- 'Yes' or 'No'
notes TEXT                            -- Additional notes
user_id TEXT DEFAULT 'default_user'  -- User identifier
```

#### 2. **custom_categories** - User-defined categories
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
name TEXT NOT NULL                    -- Category name (unique per user)
user_id TEXT NOT NULL                 -- User identifier
is_active INTEGER DEFAULT 1           -- 1 = active, 0 = soft deleted
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### 3. **budgets** - Budget limits per category
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
category TEXT NOT NULL                -- Category name
amount REAL NOT NULL                  -- Budget limit
period TEXT NOT NULL                  -- Period (YYYY-MM)
user_id TEXT NOT NULL                 -- User identifier
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### 4. **user_sessions** - Session management
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
session_id TEXT UNIQUE NOT NULL       -- Session identifier
user_id TEXT NOT NULL                 -- User identifier
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

---

## API Endpoints Documentation

### Expense Management

#### **Add Expense**
- **Method:** `POST`
- **URL:** `/add`
- **Content-Type:** `multipart/form-data`
- **Request Body:**
  ```
  date: YYYY-MM-DD (required)
  business: string (required)
  amount: float (required)
  category: string (required)
  description: string (optional)
  photo: file (optional, max 6MB)
  tags: string (optional, comma-separated)
  is_recurring: 'Yes'/'No' (optional, default 'No')
  notes: string (optional)
  ```
- **Response:** Redirect to home page with success message
- **Budget Alerts:** Returns budget warnings if category limit exceeded

#### **Get Expenses (Filtered)**
- **Method:** `GET`
- **URL:** `/month-data`
- **Query Parameters:**
  - `month` (optional): YYYY-MM format
  - `category` (optional): category name
  - `tag` (optional): tag to filter by
  - `is_recurring` (optional): 'Yes'/'No'
- **Response:**
  ```json
  [
    {
      "id": 1,
      "date": "2024-01-15",
      "business": "Walmart",
      "amount": 125.50,
      "category": "Groceries",
      "description": "Weekly shopping",
      "tags": "food,weekly",
      "is_recurring": "No",
      "notes": "Bought organic"
    }
  ]
  ```

#### **Edit Expense**
- **Method:** `POST`
- **URL:** `/edit/<int:expense_id>`
- **Content-Type:** `multipart/form-data`
- **Request Body:** Same as Add Expense
- **Response:** Redirect to recent expenses with success message

#### **Delete Expense**
- **Method:** `POST`
- **URL:** `/delete/<int:expense_id>`
- **Response:** Redirect to recent expenses with success message

#### **Get Expense by ID**
- **Method:** `GET`
- **URL:** `/api/expense/<int:expense_id>`
- **Response:**
  ```json
  {
    "id": 1,
    "date": "2024-01-15",
    "business": "Walmart",
    "amount": 125.50,
    "category": "Groceries",
    "description": "Weekly shopping",
    "tags": "food,weekly",
    "is_recurring": "No",
    "notes": "Bought organic"
  }
  ```

#### **Get Overview Data**
- **Method:** `GET`
- **URL:** `/overview-data`
- **Response:**
  ```json
  {
    "months": ["2024-01", "2024-02"],
    "totals": [1250.50, 980.30]
  }
  ```

#### **Get Monthly Category Breakdown**
- **Method:** `GET`
- **URL:** `/monthly-category-data`
- **Query Parameters:**
  - `month`: YYYY-MM format (required)
- **Response:**
  ```json
  {
    "categories": ["Groceries", "Gas/Car", "Restaurants"],
    "amounts": [450.00, 200.50, 180.00]
  }
  ```

### Category Management

#### **List Categories**
- **Method:** `GET`
- **URL:** `/api/categories`
- **Response:**
  ```json
  [
    {
      "id": 1,
      "name": "Groceries",
      "is_active": 1,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
  ```

#### **Create Category**
- **Method:** `POST`
- **URL:** `/api/categories`
- **Content-Type:** `application/json`
- **Request Body:**
  ```json
  {
    "name": "Entertainment"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Category created successfully",
    "id": 8
  }
  ```

#### **Update Category**
- **Method:** `PUT`
- **URL:** `/api/categories/<int:category_id>`
- **Content-Type:** `application/json`
- **Request Body:**
  ```json
  {
    "name": "Entertainment & Media"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Category updated successfully"
  }
  ```

#### **Delete Category**
- **Method:** `DELETE`
- **URL:** `/api/categories/<int:category_id>`
- **Response:**
  ```json
  {
    "success": true,
    "message": "Category deleted successfully"
  }
  ```
- **Note:** Returns error if category is in use by existing expenses

### Budget Management

#### **List Budgets**
- **Method:** `GET`
- **URL:** `/api/budgets`
- **Response:**
  ```json
  [
    {
      "id": 1,
      "category": "Groceries",
      "amount": 500.00,
      "period": "2024-01",
      "created_at": "2024-01-01T00:00:00"
    }
  ]
  ```

#### **Create Budget**
- **Method:** `POST`
- **URL:** `/api/budgets`
- **Content-Type:** `application/json`
- **Request Body:**
  ```json
  {
    "category": "Groceries",
    "amount": 500.00,
    "period": "2024-01"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Budget created successfully",
    "id": 1
  }
  ```

#### **Update Budget**
- **Method:** `PUT`
- **URL:** `/api/budgets/<int:budget_id>`
- **Content-Type:** `application/json`
- **Request Body:**
  ```json
  {
    "amount": 600.00
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Budget updated successfully"
  }
  ```

#### **Delete Budget**
- **Method:** `DELETE`
- **URL:** `/api/budgets/<int:budget_id>`
- **Response:**
  ```json
  {
    "success": true,
    "message": "Budget deleted successfully"
  }
  ```

#### **Get Budget Status**
- **Method:** `GET`
- **URL:** `/api/budget-status`
- **Response:**
  ```json
  [
    {
      "category": "Groceries",
      "budget": 500.00,
      "spent": 450.00,
      "remaining": 50.00,
      "percentage": 90,
      "status": "warning"
    }
  ]
  ```
- **Status Values:** `"ok"` (<80%), `"warning"` (80-100%), `"exceeded"` (>100%)

### Import/Export

#### **Export to CSV**
- **Method:** `GET`
- **URL:** `/api/export-csv`
- **Response:** CSV file download
- **Headers:** `date,business,amount,category,description,tags,is_recurring,notes`

#### **Export to PDF**
- **Method:** `GET`
- **URL:** `/api/export-pdf`
- **Response:** PDF file download
- **Content:** Formatted expense report with totals and breakdown

#### **Import from CSV**
- **Method:** `POST`
- **URL:** `/api/import-csv`
- **Content-Type:** `multipart/form-data`
- **Request Body:**
  ```
  file: CSV file (required)
  ```
- **Response:**
  ```json
  {
    "success": true,
    "imported": 15,
    "skipped": 2,
    "errors": 1,
    "details": [
      "Row 3: Invalid date format",
      "Row 5: Duplicate entry detected"
    ]
  }
  ```

### Authentication

#### **Logout**
- **Method:** `GET`
- **URL:** `/logout`
- **Response:** Redirect to home page with session cleared

---

## Usage Guide

### 1. Adding Expenses

1. **Navigate to Add Purchase**
   - Click "Add Purchase" in the navigation menu

2. **Fill in Required Fields**
   - **Date**: Select or enter date (YYYY-MM-DD)
   - **Business**: Enter vendor/business name
   - **Amount**: Enter expense amount (e.g., 125.50)
   - **Category**: Start typing to see autocomplete suggestions

3. **Optional Fields**
   - **Description**: Brief description of purchase
   - **Tags**: Add comma-separated tags (e.g., "work, travel, client")
   - **Recurring**: Check if it's a subscription/recurring expense
   - **Notes**: Add detailed notes
   - **Receipt**: Upload receipt photo (JPG, PNG, max 6MB)

4. **Submit**
   - Click "Add Purchase" button
   - You'll see budget alerts if any category limit is exceeded
   - Redirected to home page with success message

**Keyboard Shortcuts:**
- `Tab` to navigate between fields
- `Enter` to submit form (when all required fields are filled)

---

### 2. Editing Expenses

1. **Navigate to Recent Expenses**
   - Click "View Recent" in the navigation menu

2. **Find the Expense**
   - Use filters to narrow down (optional)
   - Scroll through the list

3. **Click Edit Button**
   - Click the "✏️ Edit" button next to the expense

4. **Modify Fields**
   - Form pre-fills with current values
   - Change any fields as needed
   - Upload new receipt photo (replaces old one)

5. **Save Changes**
   - Click "Update Purchase" button
   - Redirected to recent expenses with success message

**Tips:**
- Original photo is displayed if available
- All validations apply (same as adding)
- Cancel button returns without saving

---

### 3. Deleting Expenses

1. **Navigate to Recent Expenses**
   - Click "View Recent" in the navigation menu

2. **Find the Expense**
   - Use filters if needed

3. **Click Delete Button**
   - Click the "🗑️ Delete" button

4. **Confirm Deletion**
   - Confirmation dialog appears
   - Click "OK" to confirm or "Cancel" to abort

5. **Expense Removed**
   - Redirected to recent expenses with success message
   - Budget status updates automatically

**Warning:** Deletion is permanent and cannot be undone!

---

### 4. Filtering and Searching

#### Filter by Month
1. Enter month in format: `YYYY-MM` (e.g., `2024-01`)
2. Click "Apply Filters"
3. See expenses only from that month

#### Filter by Category
1. Select category from dropdown
2. Click "Apply Filters"
3. See expenses only from that category

#### Filter by Tag
1. Enter tag name (e.g., "work")
2. Click "Apply Filters"
3. See expenses containing that tag

#### Filter by Recurring Status
1. Select "Recurring Only" or "One-time Only"
2. Click "Apply Filters"
3. See filtered results

#### Combine Filters
- Use multiple filters simultaneously
- All filters are applied together (AND logic)

#### Clear Filters
- Click "Clear Filters" button to reset all filters
- Returns to showing all expenses

#### Sorting
- Click column headers to sort:
  - **Date** (ascending/descending)
  - **Business** (A-Z / Z-A)
  - **Amount** (low to high / high to low)
  - **Category** (A-Z / Z-A)

---

### 5. Managing Categories

1. **Navigate to Manage Categories**
   - Click "Manage Categories" in the navigation menu

2. **View Existing Categories**
   - See all active categories in table
   - Default categories provided

3. **Add New Category**
   - Enter category name in the form
   - Click "Add Category"
   - Category appears in list immediately

4. **Edit Category**
   - Click "✏️ Edit" button
   - Enter new name in prompt
   - Click OK to save

5. **Delete Category**
   - Click "🗑️ Delete" button
   - Confirm deletion
   - **Note:** Cannot delete if category is used in expenses

**Best Practices:**
- Use descriptive, concise names
- Keep categories consistent (e.g., "Gas/Car" not "Gas" and "Car")
- Don't create too many categories (7-12 is optimal)

---

### 6. Setting and Managing Budgets

1. **Navigate to Manage Budgets**
   - Click "Manage Budgets" in the navigation menu

2. **View Budget Status**
   - See current month's budget status at top
   - Progress bars show spending vs. budget
   - Color coding:
     - 🟢 **Green**: Under 80% (safe)
     - 🟠 **Orange**: 80-100% (warning)
     - 🔴 **Red**: Over 100% (exceeded)

3. **Add New Budget**
   - Select category from dropdown
   - Enter budget amount
   - Period auto-fills with current month
   - Click "Add Budget"

4. **Edit Budget**
   - Click "✏️ Edit" button
   - Enter new amount
   - Click OK to save

5. **Delete Budget**
   - Click "🗑️ Delete" button
   - Confirm deletion

**Tips:**
- Budgets are monthly (auto-reset each month)
- Set realistic budgets based on past spending
- Review budget status regularly
- Adjust budgets as needed

---

### 7. Exporting Data

#### Export to CSV

1. **From Home Page**
   - Click "📥 Export to CSV" button

2. **Download File**
   - File downloads automatically
   - Named: `expenses_YYYYMMDD.csv`

3. **Open in Spreadsheet**
   - Open with Excel, Google Sheets, or any CSV viewer
   - All expenses exported with full details

**CSV Format:**
```csv
date,business,amount,category,description,tags,is_recurring,notes
2024-01-15,Walmart,125.50,Groceries,Weekly shopping,food,No,Bought organic
```

#### Export to PDF

1. **From Home Page**
   - Click "📄 Export to PDF" button

2. **Download File**
   - PDF generates and downloads
   - Named: `expense_report_YYYYMMDD.pdf`

3. **View Report**
   - Professional formatted report
   - Includes:
     - Expense list with all details
     - Total spending
     - Category breakdown
     - Date range

**Use Cases:**
- Backup your data
- Share with accountant
- Tax preparation
- Analysis in external tools
- Print hard copy

---

### 8. Importing Data from CSV

1. **Prepare CSV File**
   - Use required headers: `date,business,amount,category,description,tags,is_recurring,notes`
   - Date format: YYYY-MM-DD
   - Amount: decimal number (e.g., 125.50)
   - is_recurring: "Yes" or "No"

2. **From Home Page**
   - Click "📤 Import from CSV" button

3. **Select File**
   - Click "Choose File"
   - Select your CSV file
   - Click "Import" button

4. **View Import Summary**
   - Alert shows:
     - ✅ Successfully imported records
     - ⏭️ Skipped (duplicates)
     - ❌ Errors with details

5. **Verify Data**
   - Navigate to "View Recent" to see imported expenses

**Validation Rules:**
- Date must be valid format
- Amount must be positive number
- Category must exist (creates if new)
- Duplicates (same date, business, amount) are skipped

**Error Handling:**
- Invalid rows are skipped
- Valid rows are still imported
- Detailed error report provided

---

### 9. Viewing Analytics

#### Home Page Dashboard

1. **Category Breakdown (Pie Chart)**
   - Shows all-time spending by category
   - Hover over slices for exact amounts
   - Click legend to toggle categories

2. **Monthly Trends (Line Chart)**
   - Shows spending over last 12 months
   - Hover over points for details
   - Visualize spending patterns

3. **Budget Alerts**
   - Red alert box shows exceeded budgets
   - Click category name to view details

#### Monthly Overview Page

1. **Navigate to Monthly Overview**
   - Click "Monthly Overview" in navigation

2. **View Month Selector**
   - Dropdown shows all months with data
   - Select month to view details

3. **Month Statistics**
   - Total spending for selected month
   - Category breakdown pie chart
   - Compare with other months

**Analysis Tips:**
- Look for spending spikes
- Identify high-cost categories
- Track trends over time
- Compare months to find patterns

---

## Configuration

### Environment Variables (Optional)

Create a `.env` file in the `src/` directory:

```bash
# Database
EXPENSE_TRACKER_DB=budget.db

# Server
PORT=5000
FLASK_ENV=development

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-here

# Upload Settings
MAX_UPLOAD_SIZE=6291456  # 6MB in bytes
```

### Default Configuration

If no `.env` file exists, defaults are used:
- **Database:** `budget.db` in `src/db/` directory
- **Port:** `5000`
- **Secret Key:** Random development key (regenerates on restart)
- **Max Upload:** 6MB for receipt photos

### Production Settings

**Change These Before Deploying:**

1. **SECRET_KEY** - Generate strong random key:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

2. **Database Backup** - Set up automated backups:
   ```bash
   # Cron job example (Linux)
   0 2 * * * cp /path/to/budget.db /backups/budget_$(date +\%Y\%m\%d).db
   ```

3. **HTTPS** - Enable SSL/TLS certificate

4. **Rate Limiting** - Install Flask-Limiter:
   ```bash
   pip install Flask-Limiter
   ```

---

## Screenshots

### Home Page - Dashboard
![Home Page](docs/screenshots/home.png)
*Dashboard with category breakdown, monthly trends, and budget alerts*

### Add Expense
![Add Expense](docs/screenshots/add-expense.png)
*Expense entry form with autocomplete and validation*

### Recent Expenses - Filtering
![Recent Expenses](docs/screenshots/recent-expenses.png)
*Expense list with advanced filtering and sorting*

### Category Management
![Categories](docs/screenshots/categories.png)
*Custom category management interface*

### Budget Management
![Budgets](docs/screenshots/budgets.png)
*Budget caps with visual progress indicators*

### Monthly Overview
![Monthly Overview](docs/screenshots/monthly-overview.png)
*Detailed monthly spending analysis*

### Export Options
![Export](docs/screenshots/export.png)
*CSV and PDF export functionality*

### Mobile Responsive
![Mobile View](docs/screenshots/mobile.png)
*Optimized for mobile devices*

---

## Development

### Running in Development Mode

1. **Enable Debug Mode**
   ```bash
   export FLASK_ENV=development  # macOS/Linux
   set FLASK_ENV=development     # Windows
   python app.py
   ```

2. **Hot Reload**
   - Flask auto-reloads on code changes
   - No need to restart server

3. **Debug Toolbar** (Optional)
   ```bash
   pip install flask-debugtoolbar
   ```

### Code Structure

#### Backend (`app.py`)
- **Routes:** URL endpoints mapped to functions
- **Database:** SQLite queries with parameterization
- **Session Management:** Flask session for user tracking
- **File Handling:** Werkzeug secure filename and validation
- **PDF Generation:** ReportLab canvas and table

#### Frontend (JavaScript)
- **Modular:** Each page has dedicated JS file
- **Fetch API:** For async requests
- **Chart.js:** For data visualization
- **Vanilla JS:** No jQuery or framework dependencies

#### Templates (Jinja2)
- **Inheritance:** Base template with blocks
- **Context:** Python data passed to templates
- **Loops/Conditionals:** Dynamic content rendering

### Database Operations

#### Create Tables
```bash
python db/init_db.py
```

#### Reset Database
```bash
rm db/budget.db
python db/init_db.py
```

#### Query Database Directly
```bash
sqlite3 db/budget.db
.tables
SELECT * FROM purchases LIMIT 5;
.quit
```

### Testing (Placeholder for Future)

**Unit Tests:**
```bash
# Future implementation
pytest tests/
```

**Integration Tests:**
```bash
# Future implementation
pytest tests/integration/
```

**Coverage Report:**
```bash
# Future implementation
pytest --cov=app tests/
```

---

## Troubleshooting

### Common Issues

#### 1. Database Not Found
**Error:** `sqlite3.OperationalError: unable to open database file`

**Solution:**
```bash
cd src
python db/init_db.py
```

#### 2. Port Already in Use
**Error:** `OSError: [Errno 48] Address already in use`

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process or change port
export PORT=8080
python app.py
```

#### 3. Module Not Found
**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 4. ReportLab Installation Error
**Error:** `error: command 'gcc' failed with exit status 1`

**Solution (Linux):**
```bash
sudo apt-get install build-essential python3-dev
pip install reportlab
```

**Solution (macOS):**
```bash
brew install freetype
pip install reportlab
```

#### 5. CSV Import Fails
**Error:** "Invalid date format" or "Missing required fields"

**Solution:**
- Check CSV headers match exactly: `date,business,amount,category,description,tags,is_recurring,notes`
- Verify date format is YYYY-MM-DD
- Ensure no extra commas in text fields
- Use UTF-8 encoding

#### 6. Receipt Upload Fails
**Error:** "File too large" or "Invalid file type"

**Solution:**
- Ensure file is under 6MB
- Use JPG, JPEG, or PNG format
- Compress image if necessary

#### 7. Charts Not Displaying
**Error:** Blank chart area or loading indicator stuck

**Solution:**
- Check browser console for JavaScript errors (F12)
- Verify Chart.js CDN is accessible
- Clear browser cache (Ctrl+Shift+R)
- Ensure expenses exist in database

#### 8. Session Timeout
**Error:** "Please log in" message appears

**Solution:**
- Session expired (default: browser close)
- Navigate to home page to auto-login
- Check if cookies are enabled

### Debug Mode

Enable debug output in `app.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

**Warning:** Never enable debug mode in production!

### Getting Help

1. **Check Logs:** Terminal output shows Flask logs
2. **Browser Console:** F12 → Console tab for JavaScript errors
3. **Database Inspection:** Use SQLite browser or CLI
4. **Documentation:** Review API endpoints and usage guide
5. **Create Issue:** Submit detailed issue on repository

---

## Future Enhancements

### Planned Features

#### Authentication & Multi-User
- [ ] User registration and login system
- [ ] Password hashing (bcrypt)
- [ ] Password reset via email
- [ ] User profile management
- [ ] OAuth integration (Google, GitHub)

#### Advanced Budget Features
- [ ] Budget rollover (unused budget to next month)
- [ ] Budget templates (copy to other months)
- [ ] Budget forecasting based on trends
- [ ] Smart budget suggestions using AI
- [ ] Yearly budget planning

#### Category Enhancements
- [ ] Category icons/colors
- [ ] Category hierarchy (subcategories)
- [ ] Merge duplicate categories
- [ ] Category usage analytics
- [ ] Default categories per user

#### Recurring Expenses
- [ ] Automatic recurring expense creation
- [ ] Reminder notifications for upcoming recurring expenses
- [ ] Recurring expense calendar view
- [ ] Edit future occurrences

#### Reminders & Notifications
- [ ] Email notifications for budget alerts
- [ ] SMS notifications (Twilio integration)
- [ ] Push notifications (PWA)
- [ ] Payment due reminders
- [ ] Custom reminder rules

#### Analytics & Reports
- [ ] Yearly comparison reports
- [ ] Category trends over time
- [ ] Spending heatmap calendar
- [ ] AI-powered spending insights
- [ ] Export to Excel with charts
- [ ] Scheduled report emails

#### Import Integrations
- [ ] Bank account integration (Plaid API)
- [ ] Credit card statement import
- [ ] Email receipt parsing (Gmail API)
- [ ] Mobile app receipt scanning (OCR)
- [ ] Zapier integration

#### Mobile App
- [ ] React Native iOS/Android app
- [ ] Offline mode with sync
- [ ] Camera receipt capture
- [ ] Widget for quick expense entry
- [ ] Biometric authentication

#### Collaboration
- [ ] Shared budgets (family/roommates)
- [ ] Expense splitting
- [ ] Approval workflows
- [ ] Comments on expenses
- [ ] Activity log

#### Advanced Features
- [ ] Multi-currency support with exchange rates
- [ ] Tax category tagging
- [ ] Receipt OCR for automatic data extraction
- [ ] Voice input for expense entry
- [ ] Dark mode theme
- [ ] Custom date ranges for reports
- [ ] Expense search with full-text
- [ ] Bulk edit/delete operations
- [ ] Data encryption at rest

#### Performance & Scalability
- [ ] PostgreSQL migration option
- [ ] Redis caching for sessions
- [ ] API rate limiting
- [ ] Horizontal scaling support
- [ ] CDN for static assets

---

## Version Control

### Current Version
**v2.1.0** - Enhanced Edition with CRUD Operations (2024)

### Repository Information
- **Repository:** `github_test_task`
- **Branch:** `dev_branch`
- **Main Branch:** `main` (production)

### Branching Strategy
- `main` - Production-ready code
- `dev_branch` - Development and new features
- `feature/*` - Individual feature branches
- `hotfix/*` - Urgent production fixes

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Build process or auxiliary tool changes

**Example:**
```
feat(expenses): Add edit and delete functionality

- Implemented edit expense endpoint
- Added delete confirmation dialog
- Updated UI with action buttons

Closes #123
```

---

## Changelog

### v2.1.0 - Enhanced CRUD Edition (2024-Current)
- ✨ **NEW**: Full CRUD operations for expenses (edit, delete)
- ✨ **NEW**: Advanced filtering and sorting on recent expenses
- ✨ **NEW**: PDF export with professional formatting
- ✨ **NEW**: Mobile-responsive design optimized for all devices
- ✨ **NEW**: Toast notifications for better user feedback
- ✨ **NEW**: Confirmation dialogs for destructive actions
- 🎨 **IMPROVED**: Enhanced UI/UX with modern design
- 🎨 **IMPROVED**: Better form validation with helpful messages
- 🐛 **FIXED**: Date format issues in CSV import
- 🐛 **FIXED**: Budget calculation accuracy
- 📝 **DOCS**: Comprehensive API documentation
- 📝 **DOCS**: Detailed usage guide with screenshots

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

### v1.0.0 - Initial Release (2024)
- ✨ Basic expense tracking
- ✨ Monthly overview with charts
- ✨ Category-based analytics
- ✨ Receipt photo upload
- ✨ Chart.js visualizations
- 📱 Basic responsive design

---

## Contributing

We welcome contributions! Follow these steps:

### 1. Fork & Clone
```bash
git clone <your-fork-url>
cd personal-expense-tracker
```

### 2. Create Feature Branch
```bash
git checkout dev_branch
git pull origin dev_branch
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Write clean, documented code
- Follow existing code style
- Add comments for complex logic
- Update README if needed

### 4. Test Changes
```bash
# Run application
python src/app.py

# Test manually
# - Add/edit/delete expenses
# - Test filters and sorting
# - Try CSV import/export
# - Check budget alerts
```

### 5. Commit Changes
```bash
git add .
git commit -m "feat(scope): description of changes"
```

### 6. Push & Create PR
```bash
git push origin feature/your-feature-name
```
- Create Pull Request to `dev_branch`
- Describe changes in detail
- Link related issues

### 7. Code Review
- Address reviewer feedback
- Update code as needed
- Ensure CI passes (when implemented)

### Code Style Guidelines
- **Python:** PEP 8 (use `black` formatter)
- **JavaScript:** ES6+ with const/let
- **HTML:** Semantic tags, proper indentation
- **CSS:** BEM naming convention

---

## Support

### Documentation Resources
- **Confluence Hub:** [Personal Expense Tracker Documentation](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/18513929/Personal+Expense+Tracker+-+Documentation)
- **FRD:** [Functional Requirements](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/19038209/FRD+-+Personal+Expense+Tracker)
- **Architecture:** [System Architecture](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/19070977/Architecture+-+Personal+Expense+Tracker)
- **Design (HLD & LLD):** [High and Low Level Design](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/19103745/Design+HLD+LLD+-+Personal+Expense+Tracker)
- **Wireframes:** [UI Wireframes](https://epam-team-hjbw82e3.atlassian.net/wiki/spaces/~71202032a8c2ce98634c7eb966e4019e7b3bea/pages/18219028/Wireframes+-+Personal+Expense+Tracker)

### Getting Help

1. **Check Documentation**
   - README (this file)
   - API Endpoints section
   - Usage Guide
   - Troubleshooting section

2. **Search Existing Issues**
   - Check repository issues for similar problems
   - Look for solutions in closed issues

3. **Create New Issue**
   - Use issue template
   - Provide details:
     - Steps to reproduce
     - Expected vs actual behavior
     - Screenshots if applicable
     - Browser/OS information
     - Error messages

4. **Ask Team**
   - Post in team Slack channel
   - Schedule office hours with maintainers

### Bug Report Template
```markdown
**Description:**
Brief description of the bug

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Screenshots:**
If applicable

**Environment:**
- Browser: Chrome 120
- OS: Windows 11
- App Version: v2.1.0
```

---

## License
Internal EPAM project - All rights reserved

**Confidentiality Notice:** This application and its source code are proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

## Security

### Reporting Security Issues
**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email security team: security@example.com
2. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (optional)

### Security Best Practices

#### For Users
- Use strong, unique passwords (when authentication is implemented)
- Log out after using shared computers
- Keep software updated
- Don't share credentials

#### For Developers
- Never commit sensitive data (keys, passwords)
- Use environment variables for secrets
- Review code for security issues
- Keep dependencies updated
- Follow OWASP Top 10 guidelines

---

## Acknowledgments

### Technologies & Libraries
- **Flask** - Micro web framework
- **SQLite** - Embedded database
- **Chart.js** - Interactive charts
- **ReportLab** - PDF generation
- **python-dateutil** - Date parsing

### Contributors
- Development Team - EPAM Systems
- QA Team - Testing and validation
- Design Team - UI/UX design

### Inspiration
Built to solve real-world personal finance tracking needs with simplicity and power.

---

## Contact

### Project Team
- **Project Lead:** [Name]
- **Tech Lead:** [Name]
- **Developers:** [Names]

### Communication Channels
- **Slack:** #expense-tracker-team
- **Email:** expense-tracker@example.com
- **Confluence:** [Project Space]

---

**Built with ❤️ for better personal finance management**

*Last Updated: 2024 | Version 2.1.0*