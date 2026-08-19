"""
Filtering and Search UI
Implements: Advanced filtering, search, and pagination for expenses
Ticket: SCRUM-93
"""

import streamlit as st
from datetime import datetime, date, timedelta
import requests
import pandas as pd
from typing import Dict, Optional


def filter_tab(api_url: str, auth_headers: Dict[str, str]):
    """
    Filter and Search Tab
    Enhancement: SCRUM-93 (Filtering)
    """
    
    st.header("🔍 Filter & Search Expenses")
    st.markdown("Use advanced filters to find specific expenses")
    st.markdown("---")
    
    # Filter form
    with st.form(key="filter_form"):
        st.subheader("Filter Criteria")
        
        # Date range filters
        col1, col2 = st.columns(2)
        
        with col1:
            filter_start_date = st.date_input(
                "Start Date",
                value=date.today() - timedelta(days=30),
                max_value=date.today(),
                help="Filter expenses from this date"
            )
        
        with col2:
            filter_end_date = st.date_input(
                "End Date",
                value=date.today(),
                max_value=date.today(),
                help="Filter expenses until this date"
            )
        
        # Category and status filters
        col3, col4 = st.columns(2)
        
        with col3:
            # Fetch categories
            try:
                cat_response = requests.get(
                    f"{api_url}/api/categories",
                    headers=auth_headers
                )
                if cat_response.status_code == 200:
                    categories = [cat['name'] for cat in cat_response.json()]
                else:
                    categories = ["Food", "Rent", "Shopping", "Entertainment", "Other"]
            except:
                categories = ["Food", "Rent", "Shopping", "Entertainment", "Other"]
            
            filter_category = st.selectbox(
                "Category",
                options=["All"] + categories,
                help="Filter by expense category"
            )
        
        with col4:
            filter_status = st.selectbox(
                "Status",
                options=["All", "approved", "pending", "rejected"],
                help="Filter by approval status"
            )
        
        # Amount range filters
        col5, col6 = st.columns(2)
        
        with col5:
            filter_min_amount = st.number_input(
                "Min Amount ($)",
                min_value=0.0,
                value=0.0,
                step=10.0,
                help="Minimum expense amount"
            )
        
        with col6:
            filter_max_amount = st.number_input(
                "Max Amount ($)",
                min_value=0.0,
                value=10000.0,
                step=10.0,
                help="Maximum expense amount"
            )
        
        # Pagination settings
        col7, col8, col9 = st.columns([1, 1, 2])
        
        with col7:
            page_number = st.number_input(
                "Page",
                min_value=1,
                value=st.session_state.get('current_page', 1),
                step=1
            )
        
        with col8:
            page_size = st.selectbox(
                "Items per page",
                options=[10, 25, 50, 100],
                index=1
            )
        
        with col9:
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Submit button
        submit_filter = st.form_submit_button(
            "🔍 Apply Filters",
            use_container_width=True,
            type="primary"
        )
    
    # Process filter request
    if submit_filter or 'filtered_expenses' in st.session_state:
        st.markdown("---")
        
        # Build filter payload
        filter_payload = {
            "start_date": filter_start_date.isoformat() if filter_start_date else None,
            "end_date": filter_end_date.isoformat() if filter_end_date else None,
            "category": filter_category if filter_category != "All" else None,
            "status": filter_status if filter_status != "All" else None,
            "min_amount": filter_min_amount if filter_min_amount > 0 else None,
            "max_amount": filter_max_amount if filter_max_amount < 10000 else None
        }
        
        # Remove None values
        filter_payload = {k: v for k, v in filter_payload.items() if v is not None}
        
        if submit_filter:
            with st.spinner("🔍 Searching expenses..."):
                try:
                    response = requests.post(
                        f"{api_url}/api/expenses/filter?page={page_number}&page_size={page_size}",
                        json=filter_payload,
                        headers=auth_headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.filtered_expenses = result['expenses']
                        st.session_state.pagination_info = result['pagination']
                        st.session_state.current_page = page_number
                        st.session_state.filter_active = True
                    else:
                        st.error("Failed to filter expenses")
                        return
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    return
        
        # Display results
        if st.session_state.get('filter_active'):
            expenses = st.session_state.get('filtered_expenses', [])
            pagination = st.session_state.get('pagination_info', {})
            
            # Results summary
            st.subheader("📊 Search Results")
            
            summary_cols = st.columns(4)
            
            with summary_cols[0]:
                st.metric("Total Found", pagination.get('total_count', 0))
            
            with summary_cols[1]:
                st.metric("Current Page", pagination.get('page', 1))
            
            with summary_cols[2]:
                st.metric("Total Pages", pagination.get('total_pages', 1))
            
            with summary_cols[3]:
                if expenses:
                    total_amount = sum([exp['amount'] for exp in expenses])
                    st.metric("Page Total", f"${total_amount:.2f}")
            
            st.markdown("---")
            
            # Display expenses
            if expenses:
                # Convert to DataFrame for better display
                df_expenses = pd.DataFrame(expenses)
                
                # Format columns
                df_display = df_expenses[['expense_date', 'amount', 'category', 'notes', 'status']].copy()
                df_display.columns = ['Date', 'Amount', 'Category', 'Notes', 'Status']
                
                # Format amount
                df_display['Amount'] = df_display['Amount'].apply(lambda x: f"${float(x):.2f}")
                
                # Display table with enhanced configuration
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
                        "Amount": st.column_config.TextColumn("Amount"),
                        "Category": st.column_config.TextColumn("Category"),
                        "Notes": st.column_config.TextColumn("Notes"),
                        "Status": st.column_config.TextColumn("Status")
                    }
                )
                
                # Pagination controls
                st.markdown("---")
                pag_cols = st.columns([1, 1, 1, 2])
                
                with pag_cols[0]:
                    if st.button("⬅️ Previous", disabled=pagination.get('page', 1) <= 1):
                        st.session_state.current_page = pagination.get('page', 1) - 1
                        st.rerun()
                
                with pag_cols[1]:
                    if st.button("➡️ Next", disabled=pagination.get('page', 1) >= pagination.get('total_pages', 1)):
                        st.session_state.current_page = pagination.get('page', 1) + 1
                        st.rerun()
                
                with pag_cols[2]:
                    st.info(f"Page {pagination.get('page', 1)} of {pagination.get('total_pages', 1)}")
                
                # Export filtered results
                st.markdown("---")
                st.subheader("📥 Export Filtered Results")
                
                if st.button("📄 Export to CSV", use_container_width=False):
                    import io
                    csv_buffer = io.StringIO()
                    df_expenses.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv_data,
                        file_name=f"filtered_expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # Summary statistics
                st.markdown("---")
                with st.expander("📊 Filtered Data Statistics"):
                    stats_cols = st.columns(3)
                    
                    with stats_cols[0]:
                        total_filtered = sum([float(exp['amount']) for exp in expenses])
                        st.metric("Total Amount (This Page)", f"${total_filtered:.2f}")
                    
                    with stats_cols[1]:
                        avg_amount = total_filtered / len(expenses) if expenses else 0
                        st.metric("Average Amount", f"${avg_amount:.2f}")
                    
                    with stats_cols[2]:
                        unique_categories = len(set([exp['category'] for exp in expenses]))
                        st.metric("Unique Categories", unique_categories)
            
            else:
                st.info("🔍 No expenses found matching your filters")
                st.markdown("""
                **Suggestions:**
                - Try expanding the date range
                - Remove some filters
                - Check if you have expenses in the selected period
                """)
        
        # Clear filters button
        st.markdown("---")
        if st.button("🔄 Clear All Filters"):
            # Clear session state
            for key in ['filtered_expenses', 'pagination_info', 'current_page', 'filter_active']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    else:
        # Show help when no filters applied
        st.info("👆 Set your filter criteria above and click 'Apply Filters' to search")
        
        with st.expander("💡 Filter Tips & Examples"):
            st.markdown("""
            ### How to use filters:
            
            **Date Range:**
            - Filter expenses between specific dates
            - Example: Last month's expenses
            
            **Category:**
            - Filter by specific expense category
            - Select "All" to include all categories
            
            **Status:**
            - `approved`: Normal expenses
            - `pending`: Waiting for approval
            - `rejected`: Declined expenses
            
            **Amount Range:**
            - Set minimum and maximum amount
            - Example: Find all expenses over $100
            
            **Pagination:**
            - Navigate through large result sets
            - Adjust items per page for better viewing
            
            ### Examples:
            1. **Find large expenses:** Set Min Amount to $200
            2. **Last week's food:** Category=Food, Date range=Last 7 days
            3. **Pending approvals:** Status=pending
            """)
