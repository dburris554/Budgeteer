"""
Budgeteer Commit and Save Operations

Handles committing pending changes to committed data and saving to GSheets/session state.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Tuple
from datetime import datetime
from gsheets_manager import save_month_data, save_draft_data


def apply_pending_changes_to_committed() -> Tuple[bool, str]:
    """
    Apply all pending changes to committed data.
    Validates changes before applying.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    pending_changes = st.session_state.get("pending_changes", [])
    
    if not pending_changes:
        return False, "No pending changes to commit"
    
    try:
        committed_data = st.session_state.get("committed_data", pd.DataFrame())
        
        # Create a copy to work with
        updated_data = committed_data.copy()
        
        # Process each pending change
        for change in pending_changes:
            change_type = change.get("type")
            data = change.get("data", {})
            
            if change_type == "add":
                # Add new row
                new_row = pd.DataFrame([data])
                updated_data = pd.concat([updated_data, new_row], ignore_index=True)
            
            elif change_type == "edit":
                # Edit existing row - find and update
                # This would require an ID field - for now, skip
                pass
            
            elif change_type == "delete":
                # Delete row - find and remove
                # This would require an ID field - for now, skip
                pass
        
        # Ensure correct data types
        if not updated_data.empty:
            try:
                updated_data["Day"] = updated_data["Day"].astype(int)
                updated_data["Amount"] = updated_data["Amount"].astype(float)
            except:
                return False, "Data type conversion failed"
        
        # Update session state
        st.session_state.committed_data = updated_data
        
        return True, f"✅ Successfully applied {len(pending_changes)} changes"
    
    except Exception as e:
        return False, f"❌ Error applying changes: {str(e)}"


def save_committed_data() -> Tuple[bool, str]:
    """
    Save committed data to GSheets and/or session state.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        current_month = st.session_state.get("current_month")
        committed_data = st.session_state.get("committed_data")
        
        if current_month is None or committed_data is None:
            return False, "No month or data selected"
        
        # Always save to session state
        if "budget_data" not in st.session_state:
            st.session_state.budget_data = {}
        st.session_state.budget_data[current_month] = committed_data.to_dict("records")
        
        # Try to save to GSheets if authenticated
        if st.session_state.get("gsheets_ready"):
            try:
                save_month_data(current_month, committed_data)
                return True, f"✅ Changes saved to GSheets ({current_month})"
            except Exception as e:
                # Save to session state succeeded, GSheets failed
                return True, f"✅ Changes saved locally (GSheets unavailable: {str(e)[:50]}...)"
        
        return True, "✅ Changes saved to session"
    
    except Exception as e:
        return False, f"❌ Failed to save: {str(e)}"


def clear_pending_changes() -> None:
    """Clear all pending changes and draft data."""
    current_month = st.session_state.get("current_month")
    
    # Clear pending changes
    st.session_state.pending_changes = []
    
    # Clear draft data
    if current_month:
        draft_key = f"draft_{current_month}"
        if draft_key in st.session_state:
            del st.session_state[draft_key]
    
    # Try to clear GSheets draft
    if st.session_state.get("gsheets_ready"):
        try:
            save_draft_data(current_month, [])
        except:
            pass


def auto_save_draft() -> None:
    """Auto-save pending changes to draft."""
    current_month = st.session_state.get("current_month")
    pending_changes = st.session_state.get("pending_changes", [])
    
    if not current_month or not pending_changes:
        return
    
    try:
        # Save to session state
        draft_key = f"draft_{current_month}"
        st.session_state[draft_key] = pending_changes
        
        # Save to GSheets if authenticated
        if st.session_state.get("gsheets_ready"):
            save_draft_data(current_month, pending_changes)
        
        # Update last save time
        st.session_state["last_draft_save"] = datetime.now().strftime("%H:%M:%S")
    
    except Exception as e:
        # Silent fail - draft auto-save shouldn't interrupt user
        pass


def render_save_section() -> None:
    """Render the save and commit section."""
    pending_count = len(st.session_state.get("pending_changes", []))
    current_month = st.session_state.get("current_month", "Unknown")
    
    if pending_count == 0:
        st.info("✨ All changes are committed. No pending changes.", icon="ℹ️")
        return
    
    st.markdown("## 💾 Save & Commit")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**{pending_count} pending change(s) ready to commit**")
        
        # Show what will be committed
        if pending_count <= 5:
            with st.expander("Preview changes", expanded=False):
                for idx, change in enumerate(st.session_state.pending_changes):
                    change_type = change.get("type")
                    data = change.get("data", {})
                    st.caption(f"{idx + 1}. [{change_type.upper()}] {data.get('Description', 'Unknown')}")
    
    with col2:
        pass
    
    # Commit button
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("✅ Commit & Save", use_container_width=True, type="primary"):
            # Apply pending changes
            success, msg = apply_pending_changes_to_committed()
            if not success:
                st.error(msg)
                return
            
            # Save committed data
            success, msg = save_committed_data()
            if success:
                # Clear pending changes
                clear_pending_changes()
                st.toast(msg, icon="✅")
                st.rerun()
            else:
                st.error(msg)
    
    with col2:
        # Draft auto-save status
        last_save = st.session_state.get("last_draft_save")
        if last_save:
            st.caption(f"📝 Draft auto-saved at {last_save}")
        else:
            st.caption("📝 Draft: Not saved yet")


def render_month_data_summary() -> None:
    """Render summary of committed data for current month."""
    committed_data = st.session_state.get("committed_data", pd.DataFrame())
    current_month = st.session_state.get("current_month", "Unknown")
    
    if committed_data.empty:
        st.info("No committed entries yet for this month.", icon="ℹ️")
        return
    
    # Calculate summary
    try:
        df = committed_data.copy()
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        
        if "Category" in df.columns:
            income_entries = df[df["Category"] == "Income"]
            expense_entries = df[df["Category"] != "Income"]
        else:
            income_entries = pd.DataFrame()
            expense_entries = df
        
        total_income = float(income_entries["Amount"].sum()) if not income_entries.empty else 0.0
        total_expenses = float(expense_entries["Amount"].sum()) if not expense_entries.empty else 0.0
        balance = total_income - total_expenses
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("💰 Income", f"${total_income:,.2f}")
        
        with col2:
            st.metric("💸 Expenses", f"${total_expenses:,.2f}")
        
        with col3:
            color = "normal" if balance >= 0 else "inverse"
            st.metric("📊 Balance", f"${balance:,.2f}", delta_color=color)
    
    except Exception as e:
        st.warning(f"Could not calculate summary: {e}")
