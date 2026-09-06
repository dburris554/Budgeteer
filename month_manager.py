"""
Budgeteer Month Manager

Handles month selection, switching, and creation.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from gsheets_manager import (
    load_month_data, save_draft_data, get_available_months, 
    create_new_month, BUDGET_COLUMNS
)


def get_current_month_default() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.now().strftime("%Y-%m")


def initialize_month_state() -> None:
    """Initialize month-related session state variables."""
    if "current_month" not in st.session_state:
        st.session_state.current_month = get_current_month_default()
    
    if "committed_data" not in st.session_state:
        st.session_state.committed_data = pd.DataFrame(columns=BUDGET_COLUMNS)
    
    if "pending_changes" not in st.session_state:
        st.session_state.pending_changes = []
    
    if "last_draft_save" not in st.session_state:
        st.session_state.last_draft_save = None
    
    if "committed_edit_index" not in st.session_state:
        st.session_state.committed_edit_index = None


def render_month_selector() -> str:
    """
    Render month selector in sidebar.
    
    Returns:
        Selected month in "YYYY-MM" format
    """
    st.sidebar.markdown("### 📅 Monthly Budget")
    
    # Get available months
    available_months = get_available_months()
    current_month = st.session_state.get("current_month", get_current_month_default())
    
    # Ensure current month is in list
    if current_month not in available_months and available_months:
        current_month = available_months[0]
    elif not available_months:
        # If no months exist, use current month
        available_months = [current_month]
    
    # Month selector dropdown
    selected_month = st.sidebar.selectbox(
        "Select Month",
        options=available_months if available_months else [current_month],
        index=(available_months.index(current_month) if current_month in available_months else 0),
        key="month_selector"
    )
    
    # Create new month button
    st.sidebar.divider()
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("➕ New Month", use_container_width=True):
            st.session_state["show_new_month_dialog"] = True
    
    with col2:
        if st.button("📋 Template", use_container_width=True):
            st.session_state["show_template_dialog"] = True
    
    return selected_month


def handle_month_creation() -> None:
    """Handle new month creation dialog."""
    if not st.session_state.get("show_new_month_dialog"):
        return
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### Create New Month")
    
    # Month input
    new_month = st.sidebar.text_input(
        "Month (YYYY-MM format)",
        placeholder=get_current_month_default(),
        key="new_month_input"
    )
    
    # Template selection
    create_from_template = st.sidebar.radio(
        "Start with:",
        options=["Blank", "Current Month", "Previous Month"],
        key="template_choice"
    )
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("Create", use_container_width=True, key="create_month_btn"):
            if not new_month:
                st.sidebar.error("❌ Please enter a month")
            elif len(new_month) != 7 or new_month[4] != '-':
                st.sidebar.error("❌ Invalid format. Use YYYY-MM")
            else:
                # Get template data if requested
                template_data = None
                if create_from_template == "Current Month":
                    template_data = st.session_state.get("committed_data")
                elif create_from_template == "Previous Month":
                    # TODO: Load previous month's data
                    pass
                
                # Create month
                if create_new_month(new_month, template_data):
                    st.sidebar.success(f"✅ Created month {new_month}")
                    st.session_state["current_month"] = new_month
                    st.session_state["show_new_month_dialog"] = False
                    st.rerun()
                else:
                    st.sidebar.error("❌ Failed to create month")
    
    with col2:
        if st.button("Cancel", use_container_width=True, key="cancel_month_btn"):
            st.session_state["show_new_month_dialog"] = False
            st.rerun()


def switch_month(new_month: str) -> None:
    """
    Switch to a different month.
    Auto-saves current pending changes to draft before switching.
    
    Args:
        new_month: Month in "YYYY-MM" format
    """
    if new_month == st.session_state.get("current_month"):
        return  # Already on this month
    
    # Save current month's draft before switching
    current_month = st.session_state.get("current_month")
    if current_month and st.session_state.get("pending_changes"):
        save_draft_data(current_month, st.session_state.pending_changes)
        st.toast(f"💾 Draft saved for {current_month}")
    
    # Switch to new month
    st.session_state.current_month = new_month
    
    # Load new month's committed data
    st.session_state.committed_data = load_month_data(new_month)
    
    # Initialize pending changes for new month (or load from draft)
    st.session_state.pending_changes = []  # TODO: Load from draft if exists
    
    st.toast(f"📅 Switched to {new_month}", icon="✅")


def get_month_summary(df: pd.DataFrame) -> dict:
    """
    Calculate summary statistics for a month's data.
    
    Args:
        df: DataFrame with budget entries
    
    Returns:
        Dictionary with summary metrics
    """
    if df.empty:
        return {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net_balance": 0.0,
            "entry_count": 0,
            "income_count": 0,
            "expense_count": 0
        }
    
    # Ensure numeric types
    try:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    except:
        pass
    
    income_entries = df[df['Category'] == 'Income'] if 'Category' in df.columns else pd.DataFrame()
    expense_entries = df[df['Category'] != 'Income'] if 'Category' in df.columns else df
    
    total_income = float(income_entries['Amount'].sum()) if not income_entries.empty else 0.0
    total_expenses = float(expense_entries['Amount'].sum()) if not expense_entries.empty else 0.0
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": total_income - total_expenses,
        "entry_count": len(df),
        "income_count": len(income_entries),
        "expense_count": len(expense_entries)
    }


def render_month_summary_metrics() -> None:
    """Render summary metrics for current month."""
    df = st.session_state.get("committed_data", pd.DataFrame(columns=BUDGET_COLUMNS))
    summary = get_month_summary(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Income",
            f"${summary['total_income']:,.2f}",
            delta=f"{summary['income_count']} entries"
        )
    
    with col2:
        st.metric(
            "Total Expenses",
            f"${summary['total_expenses']:,.2f}",
            delta=f"{summary['expense_count']} entries"
        )
    
    with col3:
        st.metric(
            "Net Balance",
            f"${summary['net_balance']:,.2f}",
            delta="+" if summary['net_balance'] >= 0 else "-",
            delta_color="normal" if summary['net_balance'] >= 0 else "inverse"
        )
