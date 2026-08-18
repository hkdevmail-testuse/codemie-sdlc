"""
Category Management UI
Implements: CRUD operations for custom expense categories
Ticket: SCRUM-96
"""

import streamlit as st
import requests
from typing import Dict
from datetime import datetime


def category_management_tab(api_url: str, auth_headers: Dict[str, str]):
    """
    Category Management Tab
    Enhancement: SCRUM-96 (Custom Categories)
    """
    
    st.header("📋 Category Management")
    st.markdown("Manage your expense categories")
    st.markdown("---")
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("➕ Add New Category")
        
        with st.form(key="add_category_form", clear_on_submit=True):
            new_category_name = st.text_input(
                "Category Name",
                max_chars=100,
                help="Enter a unique category name (2-100 characters)"
            )
            
            new_category_desc = st.text_area(
                "Description",
                max_chars=500,
                height=100,
                help="Optional description for the category"
            )
            
            add_button = st.form_submit_button(
                "➕ Add Category",
                use_container_width=True,
                type="primary"
            )
            
            if add_button:
                if not new_category_name or len(new_category_name) < 2:
                    st.error("❌ Category name must be at least 2 characters")
                else:
                    try:
                        response = requests.post(
                            f"{api_url}/api/categories",
                            json={
                                "name": new_category_name.strip(),
                                "description": new_category_desc.strip() if new_category_desc else None
                            },
                            headers=auth_headers
                        )
                        
                        if response.status_code == 200:
                            st.success(f"✅ Category '{new_category_name}' added successfully!")
                            st.balloons()
                            # Clear cache to refresh category list
                            if 'categories_list' in st.session_state:
                                del st.session_state['categories_list']
                            st.rerun()
                        else:
                            error_detail = response.json().get('detail', 'Unknown error')
                            st.error(f"❌ Failed to add category: {error_detail}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        # Help section
        with st.expander("ℹ️ Category Guidelines"):
            st.markdown("""
            ### Category Best Practices:
            
            ✅ **Good category names:**
            - Food & Dining
            - Transportation
            - Healthcare
            - Entertainment
            - Utilities
            
            ❌ **Avoid:**
            - Too generic names
            - Duplicate names
            - Special characters
            
            **Tips:**
            - Keep names short and descriptive
            - Use consistent naming
            - Group similar expenses
            """)
    
    with col2:
        st.subheader("📂 Existing Categories")
        
        # Fetch categories
        try:
            response = requests.get(
                f"{api_url}/api/categories?active_only=false",
                headers=auth_headers
            )
            
            if response.status_code == 200:
                categories = response.json()
                st.session_state.categories_list = categories
            else:
                st.error("Failed to load categories")
                categories = []
        
        except Exception as e:
            st.error(f"Error loading categories: {str(e)}")
            categories = []
        
        # Filter options
        show_inactive = st.checkbox("Show inactive categories", value=False)
        
        # Filter categories based on checkbox
        if not show_inactive:
            categories = [cat for cat in categories if cat['is_active']]
        
        # Display categories
        if categories:
            st.info(f"📊 Showing {len(categories)} categor{'y' if len(categories) == 1 else 'ies'}")
            
            # Create tabs for active and inactive
            for idx, category in enumerate(categories):
                with st.expander(
                    f"{'✅' if category['is_active'] else '❌'} {category['name']}",
                    expanded=False
                ):
                    # Display category info
                    info_cols = st.columns([2, 1])
                    
                    with info_cols[0]:
                        st.markdown(f"**Description:** {category.get('description', 'No description')}")
                        st.caption(f"Created: {category.get('created_at', 'N/A')}")
                        st.caption(f"Status: {'Active' if category['is_active'] else 'Inactive'}")
                    
                    with info_cols[1]:
                        if category['is_active']:
                            st.success("🟢 Active")
                        else:
                            st.warning("🔴 Inactive")
                    
                    st.markdown("---")
                    
                    # Edit form
                    with st.form(key=f"edit_category_{category['id']}"):
                        st.markdown("**Edit Category**")
                        
                        edit_name = st.text_input(
                            "Name",
                            value=category['name'],
                            max_chars=100,
                            key=f"edit_name_{category['id']}"
                        )
                        
                        edit_desc = st.text_area(
                            "Description",
                            value=category.get('description', ''),
                            max_chars=500,
                            height=80,
                            key=f"edit_desc_{category['id']}"
                        )
                        
                        action_cols = st.columns([1, 1, 1])
                        
                        with action_cols[0]:
                            update_button = st.form_submit_button(
                                "💾 Update",
                                use_container_width=True
                            )
                        
                        with action_cols[1]:
                            if category['is_active']:
                                delete_button = st.form_submit_button(
                                    "🗑️ Delete",
                                    use_container_width=True
                                )
                            else:
                                delete_button = False
                        
                        with action_cols[2]:
                            st.markdown("")  # Spacer
                        
                        # Handle update
                        if update_button:
                            if not edit_name or len(edit_name) < 2:
                                st.error("Category name must be at least 2 characters")
                            else:
                                try:
                                    response = requests.put(
                                        f"{api_url}/api/categories/{category['id']}",
                                        json={
                                            "name": edit_name.strip(),
                                            "description": edit_desc.strip() if edit_desc else None
                                        },
                                        headers=auth_headers
                                    )
                                    
                                    if response.status_code == 200:
                                        st.success("✅ Category updated!")
                                        if 'categories_list' in st.session_state:
                                            del st.session_state['categories_list']
                                        st.rerun()
                                    else:
                                        error_detail = response.json().get('detail', 'Unknown error')
                                        st.error(f"❌ Update failed: {error_detail}")
                                
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                        
                        # Handle delete (admin only)
                        if delete_button:
                            try:
                                response = requests.delete(
                                    f"{api_url}/api/categories/{category['id']}",
                                    headers=auth_headers
                                )
                                
                                if response.status_code == 200:
                                    st.success("✅ Category deleted!")
                                    if 'categories_list' in st.session_state:
                                        del st.session_state['categories_list']
                                    st.rerun()
                                elif response.status_code == 403:
                                    st.error("❌ Admin privileges required to delete categories")
                                else:
                                    error_detail = response.json().get('detail', 'Unknown error')
                                    st.error(f"❌ Delete failed: {error_detail}")
                            
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
        
        else:
            st.info("📋 No categories found")
            st.markdown("Add your first category using the form on the left")
    
    # Statistics section
    st.markdown("---")
    st.subheader("📊 Category Statistics")
    
    if 'categories_list' in st.session_state:
        all_categories = st.session_state.categories_list
        
        stats_cols = st.columns(4)
        
        with stats_cols[0]:
            total_categories = len(all_categories)
            st.metric("Total Categories", total_categories)
        
        with stats_cols[1]:
            active_count = len([c for c in all_categories if c['is_active']])
            st.metric("Active", active_count)
        
        with stats_cols[2]:
            inactive_count = len([c for c in all_categories if not c['is_active']])
            st.metric("Inactive", inactive_count)
        
        with stats_cols[3]:
            with_desc = len([c for c in all_categories if c.get('description')])
            st.metric("With Description", with_desc)
    
    # Information banner
    st.markdown("---")
    st.info("""
    ### 💡 About Categories
    
    Categories help you organize and track your expenses effectively:
    
    - **Default Categories:** The system comes with common categories (Food, Rent, etc.)
    - **Custom Categories:** Add your own categories to match your spending habits
    - **Active/Inactive:** Inactive categories are hidden from new expense entry but preserve historical data
    - **Cannot Delete:** Categories with existing expenses cannot be permanently deleted (soft delete only)
    - **Admin Rights:** Deleting categories requires admin privileges for safety
    
    **Best Practice:** Create categories that match your budget structure for better insights!
    """)
    
    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Categories", use_container_width=False):
        if 'categories_list' in st.session_state:
            del st.session_state['categories_list']
        st.rerun()
