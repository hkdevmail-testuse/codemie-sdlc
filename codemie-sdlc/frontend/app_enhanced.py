"""
Enhanced Streamlit Frontend for Expense Management System
Implements: Authentication, Validation, Filtering, Export, Custom Categories
Tickets: SCRUM-92, SCRUM-93, SCRUM-94, SCRUM-95, SCRUM-96
"""

import streamlit as st
from datetime import datetime
import requests
from add_update_ui_enhanced import add_update_tab
from analytics_ui_enhanced import analytics_tab
from filter_ui import filter_tab
from category_management_ui import category_management_tab
import json

API_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Expense Tracker - Enhanced",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .success-msg {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-msg {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)


# ================================================
# Session State Initialization
# ================================================

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None


# ================================================
# Authentication Functions (SCRUM-95)
# ================================================

def login(username: str, password: str) -> bool:
    """
    Authenticate user
    Enhancement: SCRUM-95 (Security)
    """
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.token = data['access_token']
            st.session_state.user = data['user']
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False


def register(username: str, email: str, password: str) -> bool:
    """
    Register new user
    Enhancement: SCRUM-95 (Security)
    """
    try:
        response = requests.post(
            f"{API_URL}/api/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": "user"
            }
        )
        
        if response.status_code == 200:
            return True
        else:
            error_detail = response.json().get('detail', 'Registration failed')
            st.error(error_detail)
            return False
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False


def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()


def get_auth_headers():
    """Get authentication headers for API requests"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


# ================================================
# Login/Registration Page
# ================================================

def show_login_page():
    """Display login/registration page"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔐 Expense Tracker Login")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login to Your Account")
            
            with st.form("login_form"):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        with st.spinner("Authenticating..."):
                            if login(username, password):
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Invalid username or password")
            
            # Demo credentials info
            with st.expander("ℹ️ Demo Credentials"):
                st.info("""
                **Demo User:**
                - Username: `demo_user`
                - Password: `admin123`
                
                **Admin User:**
                - Username: `admin`
                - Password: `admin123`
                """)
        
        with tab2:
            st.subheader("Create New Account")
            
            with st.form("register_form"):
                reg_username = st.text_input("Username", key="reg_username", 
                                            help="Min 3 characters, letters, numbers, and underscores only")
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password",
                                            help="Min 6 characters")
                reg_password_confirm = st.text_input("Confirm Password", type="password", 
                                                    key="reg_password_confirm")
                
                submit = st.form_submit_button("Register", use_container_width=True)
                
                if submit:
                    # Validation
                    if not all([reg_username, reg_email, reg_password, reg_password_confirm]):
                        st.error("Please fill in all fields")
                    elif reg_password != reg_password_confirm:
                        st.error("Passwords do not match")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif len(reg_username) < 3:
                        st.error("Username must be at least 3 characters")
                    else:
                        with st.spinner("Creating account..."):
                            if register(reg_username, reg_email, reg_password):
                                st.success("Registration successful! Please login.")
                            else:
                                st.error("Registration failed. Username or email may already exist.")


# ================================================
# Main Application
# ================================================

def show_main_app():
    """Display main application after authentication"""
    
    # Sidebar
    with st.sidebar:
        st.title("💰 Expense Tracker")
        st.markdown("---")
        
        # User info
        if st.session_state.user:
            st.write(f"**Welcome, {st.session_state.user['username']}!**")
            st.write(f"Role: {st.session_state.user['role'].upper()}")
            st.markdown("---")
        
        # Navigation
        st.header("Navigation")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Main content tabs
    tabs = ["📝 Add/Update Expense", "📊 Analytics", "🔍 Filter & Search", "📋 Categories"]
    
    # Add admin tab if user is admin
    if st.session_state.user and st.session_state.user['role'] == 'admin':
        tabs.append("👑 Admin")
    
    selected_tab = st.tabs(tabs)
    
    # Tab 1: Add/Update Expense
    with selected_tab[0]:
        add_update_tab(API_URL, get_auth_headers())
    
    # Tab 2: Analytics
    with selected_tab[1]:
        analytics_tab(API_URL, get_auth_headers())
    
    # Tab 3: Filter & Search (SCRUM-93)
    with selected_tab[2]:
        filter_tab(API_URL, get_auth_headers())
    
    # Tab 4: Category Management (SCRUM-96)
    with selected_tab[3]:
        category_management_tab(API_URL, get_auth_headers())
    
    # Tab 5: Admin (if applicable)
    if len(selected_tab) > 4:
        with selected_tab[4]:
            st.header("👑 Admin Panel")
            st.info("Admin features coming soon...")


# ================================================
# Main Entry Point
# ================================================

def main():
    """Main application entry point"""
    
    # Check authentication status
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()


if __name__ == "__main__":
    main()
