# Quick Start Guide - Enhanced Expense Tracker

## 🚀 Get Started in 5 Minutes

This guide helps you quickly test the enhanced features of the Personal Expense Tracker.

---

## Prerequisites
- Python 3.8+
- Web browser (Chrome, Firefox, Safari, Edge)

---

## Installation

```bash
# 1. Navigate to source directory
cd src

# 2. Create virtual environment (optional but recommended)
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the enhanced application
python app_enhanced.py
```

The application will start at: **http://localhost:5000**

---

## Quick Feature Tour

### 1️⃣ Add an Expense (2 minutes)

1. Click **"Add Purchase"** in navigation
2. Fill in the form:
   - **Date:** Today's date (pre-filled)
   - **Business:** "Test Store"
   - **Amount:** 50.00
   - **Category:** "Groceries"
   - **Description:** "Testing the app"
3. Click **"Add Purchase"**
4. See success message ✅

---

### 2️⃣ View & Filter Expenses (2 minutes)

1. Click **"View Recent"** in navigation
2. See your expense in the table
3. Try the **filters**:
   - Set date range (e.g., last month to today)
   - Select a category from dropdown
   - Search by business name
   - Set min/max amount
4. Click **"Apply Filters"**
5. See filtered results
6. Click **"Clear Filters"** to reset

---

### 3️⃣ Edit an Expense (1 minute)

1. On **"View Recent"** page, find your test expense
2. Click the **"Edit"** button (green)
3. Modal dialog opens with current values
4. Change any field (e.g., amount to 75.00)
5. Click **"Save Changes"**
6. See updated expense in table ✅

---

### 4️⃣ View Analytics (1 minute)

1. Click **"Home"** in navigation
2. See two charts:
   - **Monthly Spending Trend** (line chart)
   - **Category Breakdown** (pie chart)
3. Try **date range filter**:
   - Set start date: 6 months ago
   - Set end date: today
   - Click **"Apply Date Filter"**
4. Charts update to show selected period ✅

---

### 5️⃣ Delete an Expense (1 minute)

1. Go to **"View Recent"** page
2. Find a test expense to delete
3. Click **"Delete"** button (red)
4. Confirm deletion in popup
5. Expense removed from table ✅

---

## Testing Scenarios

### Scenario A: Basic Workflow
```
Add Expense → View Recent → Edit → Save → Delete
Time: 5 minutes
```

### Scenario B: Advanced Filtering
```
1. Add 5 expenses (different categories, dates, amounts)
2. Filter by category → See only that category
3. Filter by date range → See only that period
4. Filter by amount range → See only matching amounts
5. Combine filters → See precise results
Time: 10 minutes
```

### Scenario C: Analytics Testing
```
1. Add expenses across 3 different months
2. Add expenses in 4 different categories
3. View Home page → See data in charts
4. Filter by 1-month range → Charts update
5. Filter by specific category on Recent page
Time: 10 minutes
```

---

## Feature Checklist

Use this to verify all features work:

### Core Features
- [ ] Add expense with all fields
- [ ] Add expense with only required fields
- [ ] View all expenses
- [ ] View monthly overview

### NEW: Edit Features ✨
- [ ] Open edit modal
- [ ] Edit date
- [ ] Edit business name
- [ ] Edit amount
- [ ] Edit category
- [ ] Edit description
- [ ] Save changes
- [ ] See updated data

### NEW: Delete Features ✨
- [ ] Click delete button
- [ ] Confirmation dialog appears
- [ ] Confirm deletion
- [ ] Expense removed
- [ ] Cancel deletion works

### NEW: Filter Features ✨
- [ ] Filter by start date
- [ ] Filter by end date
- [ ] Filter by date range
- [ ] Filter by category
- [ ] Search by business name
- [ ] Filter by min amount
- [ ] Filter by max amount
- [ ] Combine multiple filters
- [ ] Clear all filters

### NEW: Analytics Features ✨
- [ ] View line chart (monthly trends)
- [ ] View pie chart (category breakdown)
- [ ] Filter charts by date range
- [ ] Charts update correctly
- [ ] Reset to all-time view

### UI/UX Features
- [ ] Modal opens smoothly
- [ ] Modal closes on X click
- [ ] Modal closes on Cancel
- [ ] Buttons have hover effects
- [ ] Forms validate input
- [ ] Error messages display
- [ ] Success messages display

### Responsive Design
- [ ] Works on desktop (> 1024px)
- [ ] Works on tablet (768px - 1024px)
- [ ] Works on mobile (< 768px)
- [ ] Navigation accessible on all sizes
- [ ] Charts readable on all sizes

---

## Sample Data for Testing

### Test Expense 1
```
Date: 2024-01-15
Business: Walmart
Amount: 127.50
Category: Groceries
Description: Weekly shopping
```

### Test Expense 2
```
Date: 2024-01-20
Business: Shell Gas Station
Amount: 45.00
Category: Gas/Car
Description: Gas fill-up
```

### Test Expense 3
```
Date: 2024-02-01
Business: Target
Amount: 89.99
Category: Clothes
Description: Winter jacket
```

### Test Expense 4
```
Date: 2024-02-14
Business: Olive Garden
Amount: 67.50
Category: Restaurants
Description: Valentine's dinner
```

### Test Expense 5
```
Date: 2024-03-01
Business: Home Depot
Amount: 234.00
Category: Furniture/Home
Description: Paint supplies
```

---

## Expected Results

### After Adding Test Data Above:

**View Recent:**
- Should see 5 expenses
- Sorted by date (newest first)
- All details visible in table

**Home Analytics:**
- Line chart shows 3 months (Jan, Feb, Mar)
- Pie chart shows 5 categories
- Each category has a different color

**Filters:**
- Date range Jan 1 - Jan 31: Shows 2 expenses
- Category "Groceries": Shows 1 expense
- Amount > $100: Shows 2 expenses
- Business contains "Target": Shows 1 expense

---

## Common Test Cases

### 1. Edit Validation
```
Test: Try to save expense with negative amount
Expected: Error message
Actual: ___________
```

### 2. Delete Confirmation
```
Test: Click delete then cancel
Expected: Expense NOT deleted
Actual: ___________
```

### 3. Filter Combination
```
Test: Date range + Category + Amount
Expected: Only matching expenses shown
Actual: ___________
```

### 4. Chart Updates
```
Test: Filter analytics by 1 month
Expected: Charts show only that month
Actual: ___________
```

---

## Keyboard Shortcuts

```
Tab         : Navigate through form fields
Enter       : Submit form
Esc         : Close modal (planned)
Ctrl + F    : Browser search (use for finding expenses)
```

---

## Browser Console

### Check for Errors
```
F12 (Windows/Linux) or Cmd+Opt+I (Mac)
→ Console tab
→ Look for red error messages
```

### Network Activity
```
F12 → Network tab
→ Filter: XHR
→ See API calls
→ Check request/response
```

---

## API Testing (Optional)

### Using curl:

```bash
# Get all expenses
curl http://localhost:5000/month-data

# Get filtered expenses
curl "http://localhost:5000/month-data?category=Groceries&start_date=2024-01-01"

# Get categories
curl http://localhost:5000/categories

# Get single expense
curl http://localhost:5000/purchase/1

# Update expense
curl -X PUT http://localhost:5000/purchase/1 \
  -H "Content-Type: application/json" \
  -d '{"date":"2024-01-15","business":"Updated","amount":100,"category":"Groceries","description":"Test"}'

# Delete expense
curl -X DELETE http://localhost:5000/purchase/1
```

### Using Browser DevTools:

```javascript
// In browser console on app page

// Fetch expenses
fetch('/month-data')
  .then(r => r.json())
  .then(console.log);

// Delete expense
fetch('/purchase/1', { method: 'DELETE' })
  .then(r => r.json())
  .then(console.log);
```

---

## Troubleshooting

### Issue: Application won't start
**Solution:**
```bash
# Check if port 5000 is in use
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process or use different port
export PORT=8000
python app_enhanced.py
```

### Issue: Can't see enhanced features
**Solution:**
1. Make sure you're running `app_enhanced.py`
2. Check browser is loading `script_enhanced.js`
3. Clear browser cache (Ctrl+Shift+R)
4. Check browser console for errors

### Issue: Filters don't work
**Solution:**
1. Verify you clicked "Apply Filters"
2. Check network tab for API calls
3. Verify date format is YYYY-MM-DD
4. Try clearing filters and re-applying

### Issue: Modal doesn't appear
**Solution:**
1. Check browser console for JavaScript errors
2. Verify `styles_enhanced.css` is loaded
3. Try different browser
4. Check for ad blockers interfering

---

## Performance Benchmarks

Expected response times on local machine:

| Operation | Expected Time |
|-----------|---------------|
| Load home page | < 1 second |
| Add expense | < 500ms |
| Load recent expenses | < 1 second |
| Apply filters | < 500ms |
| Edit expense (open modal) | < 200ms |
| Save edited expense | < 500ms |
| Delete expense | < 300ms |
| Load charts | < 1 second |
| Update charts with filter | < 500ms |

If experiencing slower times, check:
- Database size (> 1000 records may slow queries)
- Network connection
- Available system resources

---

## Reporting Issues

When reporting issues, include:

1. **What you did:** Step-by-step actions
2. **Expected result:** What should happen
3. **Actual result:** What actually happened
4. **Browser:** Chrome 120, Firefox 121, etc.
5. **Console errors:** Any red messages in F12 console
6. **Screenshots:** If UI issue

**Example:**
```
ISSUE: Edit modal doesn't open

Steps:
1. Added expense on Add page
2. Went to View Recent page
3. Clicked "Edit" button on expense row

Expected: Modal dialog should open
Actual: Nothing happens

Browser: Chrome 120
Console: Error: Cannot read property 'id' of undefined
Screenshot: [attached]
```

---

## Success Criteria

✅ **Testing Complete When:**

- [ ] All 5 sample expenses added
- [ ] Each expense can be edited
- [ ] Each expense can be deleted
- [ ] All filter combinations work
- [ ] Charts display correctly
- [ ] Date range filtering works
- [ ] Modal opens and closes smoothly
- [ ] No console errors
- [ ] Works on mobile viewport
- [ ] All buttons respond correctly

---

## Next Steps After Testing

### If Everything Works:
1. ✅ Mark features as verified
2. 📝 Provide feedback on UX
3. 🚀 Ready for staging deployment

### If Issues Found:
1. 📋 Document all issues
2. 🐛 Report with details above
3. 🔄 Re-test after fixes

---

## Need Help?

### Documentation:
- **Full Guide:** See README_ENHANCED.md
- **Code Review:** See CODE_REVIEW.md
- **Implementation:** See IMPLEMENTATION_SUMMARY.md

### Quick Links:
- Original README: `README.md`
- Enhanced README: `README_ENHANCED.md`
- Code Review: `CODE_REVIEW.md`

---

**Ready to test? Start with the 5-minute Quick Feature Tour above! 🚀**

**Testing Time Estimate:**
- Quick Tour: 5 minutes
- Full Testing: 30 minutes
- Comprehensive Testing: 1-2 hours

**Happy Testing! 🧪**
