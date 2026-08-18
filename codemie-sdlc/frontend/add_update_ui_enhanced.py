"""
Enhanced Add/Update Expense UI
Implements: Validation, Better UX, Dynamic Categories
Tickets: SCRUM-92, SCRUM-96
"""

import streamlit as st
from datetime import datetime, date
import requests
from typing import Dict, List


def add_update_tab(api_url: str, auth_headers: Dict[str, str]):
    """
    Enhanced Add/Update Expense Tab
    Enhancement: SCRUM-92 (Validation), SCRUM-96 (Dynamic Categories)
    """
    
    st.header("📝 Add or Update Daily Expenses")
    st.markdown("---")
    
    # Fetch categories from API (SCRUM-96)
    @st.cache_data(ttl=300)
    def get_categories():
        try:
            response = requests.get(f"{api_url}/api/categories", headers=auth_headers)
            if response.status_code == 200:
                categories = response.json()
                return [cat['name'] for cat in categories]
            else:
                st.error("Failed to load categories")
                return ["Rent", "Food", "Shopping", "Entertainment", "Other"]
        except Exception as e:
            st.error(f"Error loading categories: {str(e)}")
            return ["Rent", "Food", "Shopping", "Entertainment", "Other"]
    
    categories = get_categories()
    
    # Date selector with better UX
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_date = st.date_input(
            "Select Date",
            value=date.today(),
            max_value=date.today(),
            help="Select the date for expense entry"
        )
    
    with col2:
        st.info(f"📅 Managing expenses for: **{selected_date.strftime('%B %d, %Y')}**")
    
    # Fetch existing expenses for the selected date
    try:
        response = requests.get(
            f"{api_url}/api/expenses/{selected_date}",
            headers=auth_headers
        )
        
        if response.status_code == 200:
            existing_expenses = response.json()
        else:
            st.error("Failed to retrieve expenses")
            existing_expenses = []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        existing_expenses = []
    
    # Display summary if expenses exist
    if existing_expenses:
        total_amount = sum([exp['amount'] for exp in existing_expenses])
        st.success(f"💰 Total expenses for this date: **${total_amount:.2f}** ({len(existing_expenses)} entries)")
    
    st.markdown("---")
    
    # Form for adding/updating expenses
    with st.form(key="expense_form", clear_on_submit=False):
        st.subheader("Enter Expenses")
        st.caption("Fill in the details below. Leave amount as 0 to skip an entry.")
        
        # Column headers
        col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
        with col1:
            st.markdown("**Amount ($)**")
        with col2:
            st.markdown("**Category**")
        with col3:
            st.markdown("**Notes**")
        with col4:
            st.markdown("**Action**")
        
        expenses = []
        num_rows = max(5, len(existing_expenses) + 1)
        
        for i in range(num_rows):
            col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
            
            # Pre-fill with existing data
            if i < len(existing_expenses):
                default_amount = float(existing_expenses[i]["amount"])
                default_category = existing_expenses[i]["category"]
                default_notes = existing_expenses[i]["notes"] or ""
            else:
                default_amount = 0.0
                default_category = categories[0] if categories else "Food"
                default_notes = ""
            
            key_prefix = f"{selected_date}_{i}"
            
            with col1:
                amount_input = st.number_input(
                    label="Amount",
                    min_value=0.0,
                    max_value=999999.99,
                    step=0.01,
                    value=default_amount,
                    key=f"{key_prefix}_amount",
                    label_visibility='collapsed',
                    help="Enter amount (max $999,999.99)"
                )
            
            with col2:
                try:
                    default_index = categories.index(default_category)
                except ValueError:
                    default_index = 0
                
                category_input = st.selectbox(
                    label="Category",
                    options=categories,
                    index=default_index,
                    key=f"{key_prefix}_category",
                    label_visibility='collapsed'
                )
            
            with col3:
                notes_input = st.text_input(
                    label="Notes",
                    value=default_notes,
                    key=f"{key_prefix}_notes",
                    label_visibility='collapsed',
                    placeholder="Optional description...",
                    max_chars=5000
                )
            
            with col4:
                if amount_input > 0:
                    st.markdown("✅")
                else:
                    st.markdown("⬜")
            
            # Add to expenses list if amount > 0
            if amount_input > 0:
                expenses.append({
                    "amount": round(amount_input, 2),
                    "category": category_input,
                    "notes": notes_input.strip() if notes_input else None
                })
        
        # Form submission
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            submit_button = st.form_submit_button(
                "💾 Save Expenses",
                use_container_width=True,
                type="primary"
            )
        
        # Handle form submission
        if submit_button:
            if not expenses:
                st.warning("⚠️ No expenses to save. Please enter at least one expense with amount > 0.")
            else:
                # Validation summary
                total_to_save = sum([exp['amount'] for exp in expenses])
                
                st.info(f"📊 Saving {len(expenses)} expense(s) totaling ${total_to_save:.2f}")
                
                # Submit to API
                try:
                    response = requests.post(
                        f"{api_url}/api/expenses/{selected_date}",
                        json=expenses,
                        headers=auth_headers
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ Expenses saved successfully!")
                        st.balloons()
                        
                        # Clear cache to refresh data
                        st.cache_data.clear()
                        
                        # Provide option to clear form
                        st.info("💡 Tip: Select a different date to enter more expenses.")
                    else:
                        error_detail = response.json().get('detail', 'Unknown error')
                        st.error(f"❌ Failed to save expenses: {error_detail}")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to the server. Please ensure the backend is running.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Additional information
    st.markdown("---")
    
    with st.expander("ℹ️ Help & Tips"):
        st.markdown("""
        ### How to use:
        1. **Select a date** using the date picker
        2. **Enter expenses** in the form (amount, category, notes)
        3. Leave amount as **0 to skip** an entry
        4. Click **Save Expenses** to update
        
        ### Validation Rules:
        - ✅ Amount must be positive and less than $999,999.99
        - ✅ Category is required and must exist
        - ✅ Notes are optional (max 5000 characters)
        - ✅ Date cannot be in the future
        
        ### Notes:
        - Saving will **replace all existing expenses** for the selected date
        - Expenses are automatically validated before saving
        - Category list is dynamically loaded from the system
        """)
    
    # Quick stats
    if existing_expenses:
        st.markdown("---")
        st.subheader("📈 Quick Stats for Selected Date")
        
        # Calculate category breakdown
        category_totals = {}
        for exp in existing_expenses:
            cat = exp['category']
            category_totals[cat] = category_totals.get(cat, 0) + float(exp['amount'])
        
        # Display as columns
        cols = st.columns(min(len(category_totals), 4))
        for idx, (cat, total) in enumerate(category_totals.items()):
            with cols[idx % 4]:
                st.metric(label=cat, value=f"${total:.2f}")
