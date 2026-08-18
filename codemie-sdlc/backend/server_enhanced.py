"""
Enhanced FastAPI Server for Expense Management System
Implements: Validation, Filtering, Export, Security, Custom Categories, Performance
Tickets: SCRUM-92, SCRUM-93, SCRUM-94, SCRUM-95, SCRUM-96, SCRUM-97
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
import db_helper_enhanced as db_helper
import jwt
import csv
import io
from decimal import Decimal

app = FastAPI(
    title="Expense Management API",
    description="Enhanced Expense Tracker with Security, Filtering, and Export features",
    version="2.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration (SCRUM-95)
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()


# ================================================
# Enums
# ================================================

class ExpenseStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    viewer = "viewer"


# ================================================
# Pydantic Models (SCRUM-92: Validation)
# ================================================

class Expense(BaseModel):
    amount: float = Field(..., gt=0, le=999999.99, description="Expense amount (must be positive)")
    category: str = Field(..., min_length=1, max_length=100, description="Expense category")
    notes: Optional[str] = Field(None, max_length=5000, description="Optional notes")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)
    
    @validator('category')
    def validate_category(cls, v):
        if not v.strip():
            raise ValueError('Category cannot be empty')
        return v.strip()


class ExpenseCreate(Expense):
    expense_date: date = Field(..., description="Date of expense")
    status: ExpenseStatus = Field(default=ExpenseStatus.approved)
    receipt_path: Optional[str] = None


class ExpenseResponse(ExpenseCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DateRange(BaseModel):
    start_date: date
    end_date: date
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.user


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class ExpenseFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category: Optional[str] = None
    status: Optional[ExpenseStatus] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)


# ================================================
# SCRUM-95: Security & Authentication
# ================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return {
        "user_id": user_id,
        "username": payload.get("username"),
        "role": payload.get("role")
    }


def require_role(required_role: str):
    """Dependency to check user role"""
    def role_checker(current_user: dict = Depends(get_current_user)):
        if not db_helper.check_user_permission(current_user['user_id'], required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        return current_user
    return role_checker


# ================================================
# Authentication Endpoints (SCRUM-95)
# ================================================

@app.post("/api/auth/register", response_model=UserResponse, tags=["Authentication"])
def register_user(user: UserCreate):
    """
    Register a new user
    Enhancement: SCRUM-95 (Security)
    """
    # Validate username
    is_valid, error_msg = db_helper.validate_username(user.username)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Validate email
    if not db_helper.validate_email(user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    user_id = db_helper.create_user(user.username, user.email, user.password, user.role.value)
    
    if user_id is None:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    return UserResponse(
        id=user_id,
        username=user.username,
        email=user.email,
        role=user.role.value,
        is_active=True
    )


@app.post("/api/auth/login", response_model=Token, tags=["Authentication"])
def login(user_login: UserLogin):
    """
    Authenticate user and return JWT token
    Enhancement: SCRUM-95 (Security)
    """
    user = db_helper.authenticate_user(user_login.username, user_login.password)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"user_id": user["id"], "username": user["username"], "role": user["role"]}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user)
    )


@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserResponse(
        id=current_user["user_id"],
        username=current_user["username"],
        email="",  # Don't expose email in this endpoint
        role=current_user["role"],
        is_active=True
    )


# ================================================
# Category Endpoints (SCRUM-96)
# ================================================

@app.get("/api/categories", response_model=List[CategoryResponse], tags=["Categories"])
def get_categories(
    active_only: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all categories
    Enhancement: SCRUM-96 (Custom Categories)
    """
    categories = db_helper.get_all_categories(active_only)
    return categories


@app.post("/api/categories", response_model=Dict[str, Any], tags=["Categories"])
def create_category(
    category: CategoryCreate,
    current_user: dict = Depends(require_role("user"))
):
    """
    Create a new custom category
    Enhancement: SCRUM-96 (Custom Categories)
    """
    category_id = db_helper.create_category(
        category.name,
        category.description,
        current_user["user_id"]
    )
    
    if category_id is None:
        raise HTTPException(status_code=400, detail="Category already exists or invalid data")
    
    return {"message": "Category created successfully", "category_id": category_id}


@app.put("/api/categories/{category_id}", tags=["Categories"])
def update_category(
    category_id: int,
    category: CategoryCreate,
    current_user: dict = Depends(require_role("user"))
):
    """
    Update existing category
    Enhancement: SCRUM-96 (Custom Categories)
    """
    success = db_helper.update_category(
        category_id,
        category.name,
        category.description,
        current_user["user_id"]
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"message": "Category updated successfully"}


@app.delete("/api/categories/{category_id}", tags=["Categories"])
def delete_category(
    category_id: int,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Delete (soft delete) a category
    Enhancement: SCRUM-96 (Custom Categories)
    Requires admin role
    """
    success = db_helper.delete_category(category_id, current_user["user_id"])
    
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {"message": "Category deleted successfully"}


# ================================================
# Enhanced Expense Endpoints
# ================================================

@app.get("/api/expenses/{expense_date}", response_model=List[Expense], tags=["Expenses"])
def get_expenses(
    expense_date: date,
    current_user: dict = Depends(get_current_user)
):
    """
    Get expenses for a specific date
    Enhancement: SCRUM-95 (Security - user isolation)
    """
    expenses = db_helper.fetch_expenses_for_date(expense_date, current_user["user_id"])
    
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from database.")
    
    return expenses


@app.post("/api/expenses/{expense_date}", tags=["Expenses"])
def add_or_update_expense(
    expense_date: date,
    expenses: List[Expense],
    current_user: dict = Depends(get_current_user)
):
    """
    Add or update expenses for a date
    Enhancement: SCRUM-92 (Validation), SCRUM-95 (Security)
    """
    try:
        # Delete existing expenses for the date
        db_helper.delete_expenses_for_date(expense_date, current_user["user_id"])
        
        # Insert new expenses with validation
        for expense in expenses:
            db_helper.insert_expense(
                expense_date,
                expense.amount,
                expense.category,
                expense.notes,
                current_user["user_id"]
            )
        
        return {"message": "Expenses updated successfully"}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update expenses: {str(e)}")


# ================================================
# SCRUM-93: Filtering & Pagination
# ================================================

@app.post("/api/expenses/filter", response_model=Dict[str, Any], tags=["Expenses"])
def filter_expenses(
    filters: ExpenseFilter,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get filtered expenses with pagination
    Enhancement: SCRUM-93 (Filtering)
    """
    filter_dict = {
        "start_date": filters.start_date,
        "end_date": filters.end_date,
        "category": filters.category,
        "status": filters.status.value if filters.status else None,
        "min_amount": filters.min_amount,
        "max_amount": filters.max_amount
    }
    
    # Remove None values
    filter_dict = {k: v for k, v in filter_dict.items() if v is not None}
    
    pagination = {
        "limit": page_size,
        "offset": (page - 1) * page_size
    }
    
    expenses = db_helper.get_filtered_expenses(
        current_user["user_id"],
        filter_dict,
        pagination
    )
    
    total_count = db_helper.get_expense_count(current_user["user_id"], filter_dict)
    total_pages = (total_count + page_size - 1) // page_size
    
    return {
        "expenses": expenses,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages
        }
    }


# ================================================
# SCRUM-97: Optimized Analytics
# ================================================

@app.post("/api/analytics/", tags=["Analytics"])
def get_analytics(
    date_range: DateRange,
    current_user: dict = Depends(get_current_user)
):
    """
    Get expense analytics with performance optimization
    Enhancement: SCRUM-97 (Performance)
    """
    data = db_helper.fetch_expense_summary(
        date_range.start_date,
        date_range.end_date,
        current_user["user_id"]
    )
    
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary")
    
    total = sum([row['total'] for row in data])
    breakdown = {}
    
    for row in data:
        percentage = (float(row['total']) / total * 100) if total != 0 else 0
        breakdown[row['category']] = {
            'total': float(row['total']),
            'percentage': round(percentage, 2),
            'count': row.get('count', 0),
            'average': float(row.get('average', 0))
        }
    
    return breakdown


# ================================================
# SCRUM-94: Export Functionality
# ================================================

@app.get("/api/expenses/export/csv", tags=["Export"])
def export_expenses_csv(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Export expenses to CSV
    Enhancement: SCRUM-94 (Export)
    """
    expenses = db_helper.export_expenses_data(
        current_user["user_id"],
        start_date,
        end_date
    )
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'id', 'expense_date', 'amount', 'category', 'notes', 'status', 'created_at'
    ])
    
    writer.writeheader()
    for expense in expenses:
        writer.writerow({
            'id': expense['id'],
            'expense_date': expense['expense_date'],
            'amount': expense['amount'],
            'category': expense['category'],
            'notes': expense['notes'] or '',
            'status': expense['status'],
            'created_at': expense['created_at']
        })
    
    output.seek(0)
    
    # Return as streaming response
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=expenses_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


@app.get("/api/expenses/export/summary", tags=["Export"])
def export_expense_summary(
    start_date: date,
    end_date: date,
    current_user: dict = Depends(get_current_user)
):
    """
    Export expense summary for reporting
    Enhancement: SCRUM-94 (Export)
    """
    summary = db_helper.fetch_expense_summary(
        start_date,
        end_date,
        current_user["user_id"]
    )
    
    total = sum([float(row['total']) for row in summary])
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_amount": round(total, 2),
            "categories": [
                {
                    "category": row['category'],
                    "total": float(row['total']),
                    "count": row.get('count', 0),
                    "average": float(row.get('average', 0)),
                    "percentage": round((float(row['total']) / total * 100) if total > 0 else 0, 2)
                }
                for row in summary
            ]
        }
    }


# ================================================
# Admin Endpoints (SCRUM-95)
# ================================================

@app.get("/api/admin/users", response_model=List[UserResponse], tags=["Admin"])
def get_all_users(current_user: dict = Depends(require_role("admin"))):
    """
    Get all users (admin only)
    Enhancement: SCRUM-95 (Security)
    """
    # Implementation would require additional db_helper function
    return []


@app.put("/api/admin/expenses/{expense_id}/status", tags=["Admin"])
def update_expense_status(
    expense_id: int,
    status: ExpenseStatus,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Update expense status (admin approval workflow)
    Enhancement: SCRUM-95 (Security)
    """
    success = db_helper.update_expense_status(
        expense_id,
        status.value,
        current_user["user_id"]
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return {"message": f"Expense status updated to {status.value}"}


# ================================================
# Health Check
# ================================================

@app.get("/api/health", tags=["System"])
def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": [
            "validation",
            "filtering",
            "export",
            "security",
            "custom_categories",
            "performance_optimization"
        ]
    }


# ================================================
# Root Endpoint
# ================================================

@app.get("/", tags=["System"])
def root():
    """API root endpoint"""
    return {
        "message": "Enhanced Expense Management API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
