"""
Test Suite for Enhanced Expense Manager
Covers: Validation, Filtering, Export, Security, Categories, Performance
Tickets: SCRUM-92, SCRUM-93, SCRUM-94, SCRUM-95, SCRUM-96, SCRUM-97
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from server_enhanced import app
from db_helper_updated import (
    validate_expense_data,
    validate_email,
    validate_username,
    hash_password,
    verify_password
)

# Test client
client = TestClient(app)

# ================================================
# SCRUM-92: Validation Tests
# ================================================

class TestValidation:
    """Test expense data validation"""
    
    def test_valid_expense_data(self):
        """Test validation with valid data"""
        is_valid, msg = validate_expense_data(
            expense_date=date.today(),
            amount=100.50,
            category="Food",
            notes="Test expense"
        )
        assert is_valid == True
        assert msg is None
    
    def test_negative_amount(self):
        """Test validation rejects negative amounts"""
        is_valid, msg = validate_expense_data(
            expense_date=date.today(),
            amount=-50.0,
            category="Food",
            notes="Test"
        )
        assert is_valid == False
        assert "negative" in msg.lower()
    
    def test_amount_exceeds_maximum(self):
        """Test validation rejects amounts > 999,999.99"""
        is_valid, msg = validate_expense_data(
            expense_date=date.today(),
            amount=1000000.00,
            category="Food",
            notes="Test"
        )
        assert is_valid == False
        assert "maximum" in msg.lower()
    
    def test_missing_category(self):
        """Test validation rejects empty category"""
        is_valid, msg = validate_expense_data(
            expense_date=date.today(),
            amount=100.0,
            category="",
            notes="Test"
        )
        assert is_valid == False
        assert "category" in msg.lower()
    
    def test_notes_too_long(self):
        """Test validation rejects notes > 5000 characters"""
        long_notes = "x" * 5001
        is_valid, msg = validate_expense_data(
            expense_date=date.today(),
            amount=100.0,
            category="Food",
            notes=long_notes
        )
        assert is_valid == False
        assert "notes" in msg.lower()
    
    def test_email_validation_valid(self):
        """Test email validation with valid email"""
        assert validate_email("test@example.com") == True
        assert validate_email("user.name@domain.co.uk") == True
    
    def test_email_validation_invalid(self):
        """Test email validation with invalid email"""
        assert validate_email("invalid") == False
        assert validate_email("@example.com") == False
        assert validate_email("test@") == False
    
    def test_username_validation_valid(self):
        """Test username validation with valid username"""
        is_valid, msg = validate_username("validuser123")
        assert is_valid == True
        assert msg is None
    
    def test_username_validation_too_short(self):
        """Test username validation rejects short usernames"""
        is_valid, msg = validate_username("ab")
        assert is_valid == False
        assert "3 characters" in msg.lower()


# ================================================
# SCRUM-95: Security Tests
# ================================================

class TestSecurity:
    """Test security features"""
    
    def test_password_hashing(self):
        """Test password hashing works"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long
    
    def test_password_verification(self):
        """Test password verification works"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True
        assert verify_password("wrongpassword", hashed) == False
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        response = client.post("/auth/register", json={
            "username": f"testuser_{date.today().strftime('%Y%m%d%H%M%S')}",
            "email": f"test_{date.today().strftime('%Y%m%d%H%M%S')}@example.com",
            "password": "password123",
            "role": "user"
        })
        
        assert response.status_code in [200, 400]  # 400 if user exists
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post("/auth/login", json={
            "username": "nonexistentuser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401


# ================================================
# SCRUM-93: Filtering Tests
# ================================================

class TestFiltering:
    """Test expense filtering functionality"""
    
    def test_filter_expenses_date_range(self):
        """Test filtering by date range"""
        response = client.post("/expenses/filter", json={
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today()),
            "limit": 50,
            "offset": 0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "expenses" in data
        assert "total_count" in data
    
    def test_filter_expenses_by_category(self):
        """Test filtering by category"""
        response = client.post("/expenses/filter", json={
            "category": "Food",
            "limit": 50,
            "offset": 0
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all returned expenses are in Food category
        for expense in data.get("expenses", []):
            assert expense["category"] == "Food"
    
    def test_filter_expenses_by_amount_range(self):
        """Test filtering by amount range"""
        response = client.post("/expenses/filter", json={
            "min_amount": 50.0,
            "max_amount": 200.0,
            "limit": 50,
            "offset": 0
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all returned expenses are within range
        for expense in data.get("expenses", []):
            amount = float(expense["amount"])
            assert 50.0 <= amount <= 200.0
    
    def test_pagination_limit(self):
        """Test pagination limit parameter"""
        response = client.post("/expenses/filter", json={
            "limit": 10,
            "offset": 0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["expenses"]) <= 10


# ================================================
# SCRUM-94: Export Tests
# ================================================

class TestExport:
    """Test export functionality"""
    
    def test_export_csv(self):
        """Test CSV export endpoint"""
        response = client.get(
            "/expenses/export/csv",
            params={
                "start_date": str(date.today() - timedelta(days=30)),
                "end_date": str(date.today())
            }
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers.get("content-disposition", "")
    
    def test_export_data_json(self):
        """Test export data endpoint (JSON)"""
        response = client.post("/expenses/export/data", json={
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today())
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "expenses" in data
        assert "count" in data
        assert isinstance(data["expenses"], list)


# ================================================
# SCRUM-96: Category Management Tests
# ================================================

class TestCategories:
    """Test category management"""
    
    def test_get_categories(self):
        """Test getting all categories"""
        response = client.get("/categories", params={"active_only": True})
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "count" in data
        assert isinstance(data["categories"], list)
    
    def test_create_category(self):
        """Test creating a new category"""
        category_name = f"TestCategory_{date.today().strftime('%Y%m%d%H%M%S')}"
        
        response = client.post("/categories", json={
            "name": category_name,
            "description": "Test category description"
        })
        
        assert response.status_code in [200, 400]  # 400 if exists
        
        if response.status_code == 200:
            data = response.json()
            assert "category_id" in data
    
    def test_create_duplicate_category(self):
        """Test creating duplicate category fails"""
        # First create a category
        category_name = f"DuplicateTest_{date.today().strftime('%Y%m%d%H%M%S')}"
        
        response1 = client.post("/categories", json={
            "name": category_name,
            "description": "First"
        })
        
        # Try to create duplicate
        response2 = client.post("/categories", json={
            "name": category_name,
            "description": "Duplicate"
        })
        
        # Second request should fail
        assert response2.status_code == 400


# ================================================
# SCRUM-97: Performance Tests
# ================================================

class TestPerformance:
    """Test performance optimizations"""
    
    def test_analytics_response_time(self):
        """Test analytics endpoint responds quickly"""
        import time
        
        start_time = time.time()
        
        response = client.post("/analytics/", json={
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today())
        })
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 2.0  # Should respond in under 2 seconds
    
    def test_filtered_expenses_response_time(self):
        """Test filtering responds quickly"""
        import time
        
        start_time = time.time()
        
        response = client.post("/expenses/filter", json={
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today()),
            "limit": 100,
            "offset": 0
        })
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond in under 1 second


# ================================================
# API Endpoint Tests
# ================================================

class TestAPIEndpoints:
    """Test all API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_get_expenses_for_date(self):
        """Test getting expenses for specific date"""
        response = client.get(f"/expenses/{date.today()}")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_add_expenses(self):
        """Test adding expenses"""
        test_expenses = [
            {
                "amount": 50.00,
                "category": "Food",
                "notes": "Test expense",
                "status": "approved"
            }
        ]
        
        response = client.post(
            f"/expenses/{date.today()}",
            json=test_expenses
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


# ================================================
# Integration Tests
# ================================================

class TestIntegration:
    """Test integrated workflows"""
    
    def test_complete_expense_workflow(self):
        """Test complete expense management workflow"""
        
        # 1. Add expenses
        test_date = date.today()
        expenses = [
            {
                "amount": 75.50,
                "category": "Food",
                "notes": "Integration test",
                "status": "approved"
            }
        ]
        
        add_response = client.post(f"/expenses/{test_date}", json=expenses)
        assert add_response.status_code == 200
        
        # 2. Retrieve expenses
        get_response = client.get(f"/expenses/{test_date}")
        assert get_response.status_code == 200
        retrieved = get_response.json()
        assert len(retrieved) > 0
        
        # 3. Filter expenses
        filter_response = client.post("/expenses/filter", json={
            "start_date": str(test_date),
            "end_date": str(test_date),
            "category": "Food",
            "limit": 10,
            "offset": 0
        })
        assert filter_response.status_code == 200
        
        # 4. Get analytics
        analytics_response = client.post("/analytics/", json={
            "start_date": str(test_date),
            "end_date": str(test_date)
        })
        assert analytics_response.status_code == 200
        
        # 5. Export data
        export_response = client.get(
            "/expenses/export/csv",
            params={
                "start_date": str(test_date),
                "end_date": str(test_date)
            }
        )
        assert export_response.status_code == 200


# ================================================
# Edge Cases and Error Handling
# ================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_invalid_date_range(self):
        """Test with end_date before start_date"""
        response = client.post("/expenses/filter", json={
            "start_date": str(date.today()),
            "end_date": str(date.today() - timedelta(days=30)),
            "limit": 10,
            "offset": 0
        })

        # Should handle gracefully - 422 is expected from Pydantic validation
        assert response.status_code in [200, 400, 422]
    
    def test_extreme_pagination(self):
        """Test with large offset"""
        response = client.post("/expenses/filter", json={
            "limit": 10,
            "offset": 10000
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "expenses" in data
    
    def test_zero_amount(self):
        """Test expense with zero amount"""
        response = client.post(f"/expenses/{date.today()}", json=[{
            "amount": 0.0,
            "category": "Food",
            "notes": "Zero amount test"
        }])
        
        # Should be rejected by validation
        assert response.status_code == 400 or response.status_code == 422
    
    def test_future_date(self):
        """Test expense with future date"""
        future_date = date.today() + timedelta(days=365)
        
        response = client.post(f"/expenses/{future_date}", json=[{
            "amount": 100.0,
            "category": "Food",
            "notes": "Future expense"
        }])
        
        # Should accept (might be planned expense)
        assert response.status_code in [200, 400]


# ================================================
# Run Tests
# ================================================

if __name__ == "__main__":
    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])
