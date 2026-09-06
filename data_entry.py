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
    st.markdown("## ✏️ Add Budget Entries")
    
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
    """Render read-only view of committed budget data with formatting."""
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
    
    # Format amount as currency for display
    if "Amount" in display_df.columns:
        try:
            display_df["Amount_display"] = display_df["Amount"].astype(float).apply(lambda x: f"${x:,.2f}")
        except:
            pass
    
    # Build column configuration
    column_config = {}
    
    if "Day" in display_df.columns:
        column_config["Day"] = st.column_config.NumberColumn(format="%d", width="small")
    
    if "Amount_display" in display_df.columns:
        column_config["Amount_display"] = st.column_config.TextColumn("Amount", width="small")
    elif "Amount" in display_df.columns:
        column_config["Amount"] = st.column_config.NumberColumn(format="$%,.2f", width="small")
    
    # Hide original Amount column if we created display version
    if "Amount_display" in display_df.columns and "Amount" in display_df.columns:
        display_df = display_df.drop(columns=["Amount"])
    
    # Display configuration for boolean columns
    for col in ["Automatic", "Paid", "Cleared"]:
        if col in display_df.columns:
            column_config[col] = st.column_config.CheckboxColumn(width="small")
    
    # Display the dataframe
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config=column_config if column_config else None,
        height=300
    )
    
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
