"""
Budgeteer Data Entry Forms

Implements form-based data entry for income and expenses.
Replaces AgGrid with native Streamlit forms for better UX and error prevention.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime


# Column schema for budget data
BUDGET_COLUMNS = ['Day', 'Description', 'Category', 'Amount', 'Allocation', 'Automatic', 'Paid', 'Cleared']


def render_income_form() -> Optional[Dict[str, Any]]:
    """
    Render form to add a new income entry.
    
    Returns:
        Dictionary with income data if submitted, None otherwise
    """
    with st.expander("➕ Add Income", expanded=False):
        with st.form("add_income_form", clear_on_submit=True):
            st.markdown("**New Income Entry**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                day = st.number_input(
                    "Day of Month",
                    min_value=1,
                    max_value=31,
                    value=1,
                    help="What day of the month will this income arrive?"
                )
                
                amount = st.number_input(
                    "Amount ($)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Income amount"
                )
            
            with col2:
                description = st.text_input(
                    "Description",
                    placeholder="e.g., Paycheck, Side Income",
                    help="Name or description of this income source"
                )
                
                allocation = st.text_input(
                    "Allocation (Bank/Source)",
                    placeholder="e.g., Chase, PayPal",
                    help="Which account or source is this deposited to?"
                )
            
            cleared = st.checkbox("Marked as Cleared", value=False)
            
            submitted = st.form_submit_button("Add Income", use_container_width=True)
            
            if submitted:
                # Validate
                if not description or not description.strip():
                    st.error("❌ Description is required")
                    return None
                
                if amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                    return None
                
                # Return income entry
                return {
                    "Day": int(day),
                    "Description": description.strip(),
                    "Category": "Income",
                    "Amount": round(amount, 2),
                    "Allocation": allocation.strip() if allocation else " ",
                    "Automatic": "False",
                    "Paid": "False",
                    "Cleared": "True" if cleared else "False"
                }
    
    return None


def render_expense_form(income_descriptions: list = None) -> Optional[Dict[str, Any]]:
    """
    Render form to add a new expense entry.
    
    Args:
        income_descriptions: List of income entry descriptions for allocation dropdown
    
    Returns:
        Dictionary with expense data if submitted, None otherwise
    """
    if income_descriptions is None:
        income_descriptions = []
    
    with st.expander("➕ Add Expense", expanded=False):
        with st.form("add_expense_form", clear_on_submit=True):
            st.markdown("**New Expense Entry**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                day = st.number_input(
                    "Day of Month",
                    min_value=1,
                    max_value=31,
                    value=1,
                    key="expense_day",
                    help="What day will this expense occur?"
                )
                
                amount = st.number_input(
                    "Amount ($)",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    key="expense_amount",
                    help="Expense amount"
                )
            
            with col2:
                description = st.text_input(
                    "Description",
                    placeholder="e.g., Rent, Groceries",
                    key="expense_description",
                    help="Name or description of this expense"
                )
                
                category = st.text_input(
                    "Category",
                    placeholder="e.g., Housing, Food, Medical",
                    key="expense_category",
                    help="Type of expense"
                )
            
            # Allocation dropdown - select which income pays for this
            st.markdown("**Paid from:**")
            if income_descriptions:
                allocation = st.selectbox(
                    "Select Income Source",
                    options=income_descriptions,
                    key="expense_allocation",
                    label_visibility="collapsed",
                    help="Which income entry should this expense be deducted from?"
                )
            else:
                allocation = st.text_input(
                    "Income Source",
                    placeholder="Enter income description",
                    key="expense_allocation_text",
                    help="Which income entry should this expense be deducted from?"
                )
                if not allocation:
                    allocation = " "
            
            # Checkboxes for flags
            col1, col2, col3 = st.columns(3)
            
            with col1:
                automatic = st.checkbox("Automatic Payment", value=False)
            
            with col2:
                paid = st.checkbox("Paid", value=False)
            
            with col3:
                cleared = st.checkbox("Cleared", value=False)
            
            submitted = st.form_submit_button("Add Expense", use_container_width=True)
            
            if submitted:
                # Validate
                if not description or not description.strip():
                    st.error("❌ Description is required")
                    return None
                
                if not category or not category.strip():
                    st.error("❌ Category is required")
                    return None
                
                if amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                    return None
                
                if not allocation or not allocation.strip():
                    st.error("❌ Must select or enter an income source")
                    return None
                
                # Return expense entry
                return {
                    "Day": int(day),
                    "Description": description.strip(),
                    "Category": category.strip(),
                    "Amount": round(amount, 2),
                    "Allocation": allocation.strip(),
                    "Automatic": "True" if automatic else "False",
                    "Paid": "True" if paid else "False",
                    "Cleared": "True" if cleared else "False"
                }
    
    return None


def render_data_entry_section() -> None:
    """Render the complete data entry section with both forms."""
    st.subheader("✏️ Add Budget Entries")
    
    # Get list of income descriptions for expense allocation dropdown
    committed_data = st.session_state.get("committed_data", pd.DataFrame())
    income_descriptions = []
    
    if not committed_data.empty and "Category" in committed_data.columns:
        income_rows = committed_data[committed_data["Category"] == "Income"]
        if not income_rows.empty and "Description" in income_rows.columns:
            income_descriptions = income_rows["Description"].unique().tolist()
    
    # Also add pending income entries
    pending_changes = st.session_state.get("pending_changes", [])
    for change in pending_changes:
        if change.get("type") == "add" and change.get("data", {}).get("Category") == "Income":
            desc = change.get("data", {}).get("Description")
            if desc and desc not in income_descriptions:
                income_descriptions.append(desc)
    
    income_descriptions.sort()
    
    # Render forms side by side
    col1, col2 = st.columns(2)
    
    with col1:
        income_entry = render_income_form()
        if income_entry:
            st.session_state.pending_changes.append({
                "type": "add",
                "data": income_entry,
                "timestamp": datetime.now().isoformat()
            })
            st.toast("✅ Income added to pending changes!", icon="✅")
            st.rerun()
    
    with col2:
        expense_entry = render_expense_form(income_descriptions)
        if expense_entry:
            st.session_state.pending_changes.append({
                "type": "add",
                "data": expense_entry,
                "timestamp": datetime.now().isoformat()
            })
            st.toast("✅ Expense added to pending changes!", icon="✅")
            st.rerun()


def render_committed_data_table() -> None:
    """Render committed budget data with edit/delete functionality."""
    committed_data = st.session_state.get("committed_data", pd.DataFrame())
    
    if committed_data.empty:
        st.info("📭 No committed entries yet. Add entries using the forms above and commit to save.", icon="ℹ️")
        return
    
    # Create display DataFrame with formatted columns
    display_df = committed_data.copy()
    
    # Ensure numeric types for calculations
    try:
        if "Day" in display_df.columns:
            display_df["Day"] = display_df["Day"].astype(int)
        if "Amount" in display_df.columns:
            display_df["Amount"] = display_df["Amount"].astype(float)
    except:
        pass
    
    # Sort by Day
    try:
        if "Day" in display_df.columns:
            display_df = display_df.sort_values("Day")
    except:
        pass
    
    # Add index for tracking
    display_df = display_df.reset_index(drop=True)
    
    # Display entries with edit/delete buttons
    for idx, (_, row) in enumerate(display_df.iterrows()):
        col1, col2, col3 = st.columns([4, 0.5, 0.5], gap="small")
        
        with col1:
            # Format and display entry
            category = row.get("Category", "")
            description = row.get("Description", "")
            amount = row.get("Amount", 0)
            day = row.get("Day", "-")
            
            if category == "Income":
                st.text(f"Day {day}: {description} (Income) - ${float(amount):,.2f}")
            else:
                st.text(f"Day {day}: {description} ({category}) - ${float(amount):,.2f}")
        
        with col2:
            if st.button("✏️", key=f"edit_committed_{idx}"):
                st.session_state.committed_edit_index = idx
                st.rerun()
        
        with col3:
            if st.button("🗑️", key=f"delete_committed_{idx}"):
                # Move to trash
                from trash import trash_item
                entry = st.session_state.committed_data.iloc[idx].to_dict()
                trash_item(entry, "committed")
                
                # Remove from committed data
                st.session_state.committed_data = st.session_state.committed_data.drop(idx)
                st.session_state.committed_data = st.session_state.committed_data.reset_index(drop=True)
                st.toast("🗑️ Entry moved to trash", icon="✅")
                st.rerun()
    
    # Show edit dialog if editing
    edit_idx = st.session_state.get("committed_edit_index")
    if edit_idx is not None and 0 <= edit_idx < len(committed_data):
        st.divider()
        render_committed_edit_dialog(edit_idx)
    
    st.divider()
    
    # Show entry count
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption(f"📊 Total Entries: {len(display_df)}")
    
    with col2:
        if "Category" in committed_data.columns:
            income_count = len(committed_data[committed_data["Category"] == "Income"])
            st.caption(f"💰 Income: {income_count}")
    
    with col3:
        if "Category" in committed_data.columns:
            expense_count = len(committed_data[committed_data["Category"] != "Income"])
            st.caption(f"💸 Expenses: {expense_count}")


def render_committed_edit_dialog(edit_index: int) -> None:
    """
    Render edit dialog for a committed entry.
    
    Args:
        edit_index: Index of entry to edit in committed_data
    """
    committed_data = st.session_state.get("committed_data", pd.DataFrame())
    
    if edit_index < 0 or edit_index >= len(committed_data):
        return
    
    entry = committed_data.iloc[edit_index]
    
    st.markdown("#### ✏️ Edit Committed Entry")
    
    with st.form(f"edit_committed_form_{edit_index}"):
        col1, col2 = st.columns(2)
        
        with col1:
            day = st.number_input(
                "Day",
                min_value=1,
                max_value=31,
                value=int(entry.get("Day", 1)),
                key=f"edit_c_day_{edit_index}"
            )
            
            amount = st.number_input(
                "Amount ($)",
                min_value=0.0,
                step=0.01,
                value=float(entry.get("Amount", 0)),
                format="%.2f",
                key=f"edit_c_amount_{edit_index}"
            )
        
        with col2:
            description = st.text_input(
                "Description",
                value=str(entry.get("Description", "")),
                key=f"edit_c_description_{edit_index}"
            )
            
            if entry.get("Category") == "Income":
                allocation = st.text_input(
                    "Allocation (Bank/Source)",
                    value=str(entry.get("Allocation", "")),
                    key=f"edit_c_allocation_{edit_index}"
                )
            else:
                category = st.text_input(
                    "Category",
                    value=str(entry.get("Category", "")),
                    key=f"edit_c_category_{edit_index}"
                )
                
                allocation = st.text_input(
                    "Allocation (Income Source)",
                    value=str(entry.get("Allocation", "")),
                    key=f"edit_c_allocation_{edit_index}"
                )
        
        # Checkboxes for flags
        col1, col2, col3 = st.columns(3)
        
        with col1:
            automatic = st.checkbox("Automatic Payment", value=entry.get("Automatic") == "True", key=f"edit_c_auto_{edit_index}")
        
        with col2:
            paid = st.checkbox("Paid", value=entry.get("Paid") == "True", key=f"edit_c_paid_{edit_index}")
        
        with col3:
            cleared = st.checkbox("Cleared", value=entry.get("Cleared") == "True", key=f"edit_c_cleared_{edit_index}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("✅ Save", use_container_width=True):
                # Update the entry
                updated_data = st.session_state.committed_data.iloc[edit_index].to_dict()
                updated_data["Day"] = int(day)
                updated_data["Amount"] = round(amount, 2)
                updated_data["Description"] = description.strip()
                updated_data["Allocation"] = allocation.strip()
                updated_data["Automatic"] = "True" if automatic else "False"
                updated_data["Paid"] = "True" if paid else "False"
                updated_data["Cleared"] = "True" if cleared else "False"
                
                if entry.get("Category") != "Income":
                    updated_data["Category"] = category.strip()
                
                # Update the DataFrame
                st.session_state.committed_data.iloc[edit_index] = pd.Series(updated_data)
                st.session_state.committed_edit_index = None
                st.toast("✅ Entry updated", icon="✅")
                st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.committed_edit_index = None
                # Small delay to allow animation
                import time
                time.sleep(0.15)
                st.rerun()


def validate_entry(entry: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a single budget entry.
    
    Args:
        entry: Dictionary with budget entry data
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["Day", "Description", "Category", "Amount", "Allocation"]
    
    for field in required_fields:
        if field not in entry or entry[field] is None:
            return False, f"Missing required field: {field}"
    
    # Validate Day
    try:
        day = int(entry["Day"])
        if day < 1 or day > 31:
            return False, "Day must be between 1 and 31"
    except (ValueError, TypeError):
        return False, "Day must be an integer"
    
    # Validate Amount
    try:
        amount = float(entry["Amount"])
        if amount < 0:
            return False, "Amount cannot be negative"
    except (ValueError, TypeError):
        return False, "Amount must be a number"
    
    # Validate Description
    if not isinstance(entry["Description"], str) or not entry["Description"].strip():
        return False, "Description cannot be empty"
    
    # Validate Category (for expenses)
    if entry.get("Category") != "Income":
        if not isinstance(entry.get("Category"), str) or not entry["Category"].strip():
            return False, "Category is required for expenses"
    
    return True, ""
