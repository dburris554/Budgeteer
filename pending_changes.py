"""
Budgeteer Pending Changes Management

Displays and manages staged changes (pending additions, edits, deletions).
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime


def initialize_pending_changes() -> None:
    """Initialize pending changes in session state."""
    if "pending_changes" not in st.session_state:
        st.session_state.pending_changes = []
    
    if "edited_change_index" not in st.session_state:
        st.session_state.edited_change_index = None


def add_pending_change(change_type: str, data: Dict[str, Any]) -> None:
    """
    Add a pending change to the list.
    
    Args:
        change_type: "add", "edit", or "delete"
        data: Change data
    """
    if "pending_changes" not in st.session_state:
        st.session_state.pending_changes = []
    
    st.session_state.pending_changes.append({
        "type": change_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })


def delete_pending_change(index: int) -> None:
    """Delete a pending change by moving it to trash."""
    if 0 <= index < len(st.session_state.get("pending_changes", [])):
        change = st.session_state.pending_changes.pop(index)
        
        # Move to trash
        from trash import trash_item
        trash_item(change, "pending")


def edit_pending_change(index: int, updated_data: Dict[str, Any]) -> None:
    """Edit a pending change."""
    if 0 <= index < len(st.session_state.get("pending_changes", [])):
        st.session_state.pending_changes[index]["data"] = updated_data
        st.session_state.pending_changes[index]["timestamp"] = datetime.now().isoformat()
        st.session_state.edited_change_index = None
        st.toast(f"✏️ Change updated", icon="✅")


def get_pending_changes_count() -> int:
    """Get count of pending changes."""
    return len(st.session_state.get("pending_changes", []))


def format_change_display(change: Dict[str, Any]) -> str:
    """
    Format a change for display.
    
    Args:
        change: Change dictionary
    
    Returns:
        Formatted string for display
    """
    change_type = change.get("type", "unknown")
    data = change.get("data", {})
    
    description = data.get("Description", "Unknown")
    amount = data.get("Amount", 0)
    day = data.get("Day", "-")
    category = data.get("Category", "")
    
    # Format based on type
    if change_type == "add":
        if category == "Income":
            return f"➕ Income: {description} - ${amount:,.2f} on day {day}"
        else:
            return f"➕ Expense: {description} ({category}) - ${amount:,.2f} on day {day}"
    elif change_type == "edit":
        return f"✏️ Edit: {description} - ${amount:,.2f}"
    elif change_type == "delete":
        return f"🗑️ Delete: {description}"
    
    return f"{change_type}: {description}"


def render_pending_changes_section() -> None:
    """Render the pending changes display section."""
    pending_changes = st.session_state.get("pending_changes", [])
    
    if not pending_changes:
        st.info("✨ No pending changes. Add entries using the forms above, or commit to finalize your budget.", icon="ℹ️")
        return
    
    st.markdown(f"##### ⏳ Pending Changes ({len(pending_changes)})")
    
    # View toggle
    view_mode = st.radio(
        "Display style:",
        options=["List", "Cards"],
        horizontal=True,
        key="pending_view_mode"
    )
    
    st.divider()
    
    # Render based on view mode
    if view_mode == "List":
        render_pending_list(pending_changes)
    else:
        render_pending_cards(pending_changes)


def render_pending_list(pending_changes: List[Dict[str, Any]]) -> None:
    """Render pending changes as a list."""
    for idx, change in enumerate(pending_changes):
        # Highlight the row being edited
        is_editing = st.session_state.get("edited_change_index") == idx
        
        if is_editing:
            # Create a container with highlight styling
            with st.container(border=True):
                col1, col2 = st.columns([4, 0.8], gap="small")
                
                with col1:
                    # Get checkbox states
                    data = change.get("data", {})
                    flags = []
                    
                    if data.get("Category") != "Income":
                        # For expenses, show the flags
                        if data.get("Automatic") == "True":
                            flags.append("⇄ Automatic")
                        if data.get("Paid") == "True":
                            flags.append("✔ Paid")
                        if data.get("Cleared") == "True":
                            flags.append("✈ Cleared")
                    else:
                        # For income, show if cleared
                        if data.get("Cleared") == "True":
                            flags.append("✈ Cleared")
                    
                    # Build display with text and flags combined
                    display_text = format_change_display(change)
                    if flags:
                        flags_str = " ".join(flags)
                        combined_html = f"""
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <span style='font-weight: bold;'>{display_text}</span>
                            <span style='background-color: #E8F0FF; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; white-space: nowrap;'>{flags_str}</span>
                        </div>
                        """
                        st.markdown(combined_html, unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='font-weight: bold;'>{display_text}</span>", unsafe_allow_html=True)
                
                with col2:
                    btn_col1, btn_col2 = st.columns(2, gap="small")
                    
                    with btn_col1:
                        if st.button("✏️", key=f"edit_{idx}", use_container_width=True):
                            st.session_state.edited_change_index = idx
                    
                    with btn_col2:
                        if st.button("🗑️", key=f"delete_{idx}", use_container_width=True):
                            delete_pending_change(idx)
                            st.rerun()
        else:
            col1, col2 = st.columns([4, 0.8], gap="small")
            
            with col1:
                # Get checkbox states
                data = change.get("data", {})
                flags = []
                
                if data.get("Category") != "Income":
                    # For expenses, show the flags
                    if data.get("Automatic") == "True":
                        flags.append("⇄ Automatic")
                    if data.get("Paid") == "True":
                        flags.append("✔ Paid")
                    if data.get("Cleared") == "True":
                        flags.append("✈ Cleared")
                else:
                    # For income, show if cleared
                    if data.get("Cleared") == "True":
                        flags.append("✈ Cleared")
                
                # Build display with text and flags combined
                display_text = format_change_display(change)
                if flags:
                    flags_str = " ".join(flags)
                    combined_html = f"""
                    <div style='display: flex; align-items: center; gap: 8px;'>
                        <span>{display_text}</span>
                        <span style='background-color: #E8F0FF; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; white-space: nowrap;'>{flags_str}</span>
                    </div>
                    """
                    st.markdown(combined_html, unsafe_allow_html=True)
                else:
                    st.text(display_text)
            
            with col2:
                btn_col1, btn_col2 = st.columns(2, gap="small")
                
                with btn_col1:
                    if st.button("✏️", key=f"edit_{idx}", use_container_width=True):
                        st.session_state.edited_change_index = idx
                
                with btn_col2:
                    if st.button("🗑️", key=f"delete_{idx}", use_container_width=True):
                        delete_pending_change(idx)
                        st.rerun()
        
        # Show edit dialog if this change is being edited
        if is_editing:
            st.divider()
            render_edit_dialog(idx)
            st.divider()


def render_pending_cards(pending_changes: List[Dict[str, Any]]) -> None:
    """Render pending changes as cards."""
    cols = st.columns(2)
    
    for idx, change in enumerate(pending_changes):
        with cols[idx % 2]:
            with st.container(border=True):
                data = change.get("data", {})
                change_type = change.get("type", "unknown")
                
                # Display change info
                if change_type == "add":
                    st.markdown(f"**➕ {data.get('Category', 'Entry')}**")
                elif change_type == "edit":
                    st.markdown(f"**✏️ Edit**")
                elif change_type == "delete":
                    st.markdown(f"**🗑️ Delete**")
                
                # Show key details
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"**Day:** {data.get('Day', '-')}")
                    st.caption(f"**Amount:** ${data.get('Amount', 0):,.2f}")
                
                with col2:
                    st.caption(f"**Description:** {data.get('Description', '-')}")
                    if data.get('Category') != 'Income':
                        st.caption(f"**Category:** {data.get('Category', '-')}")
                
                # Action buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✏️ Edit", key=f"edit_card_{idx}", use_container_width=True):
                        st.session_state.edited_change_index = idx
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_card_{idx}", use_container_width=True):
                        delete_pending_change(idx)
                        st.rerun()


def render_edit_dialog(change_index: int) -> None:
    """
    Render edit dialog for a pending change.
    
    Args:
        change_index: Index of change to edit in pending_changes list
    """
    if change_index is None or change_index < 0 or change_index >= len(st.session_state.get("pending_changes", [])):
        return
    
    change = st.session_state.pending_changes[change_index]
    data = change.get("data", {})
    
    st.markdown("#### ✏️ Edit Pending Change")
    
    with st.form(f"edit_form_{change_index}"):
        col1, col2 = st.columns(2)
        
        with col1:
            day = st.number_input(
                "Day",
                min_value=1,
                max_value=31,
                value=int(data.get("Day", 1)),
                key=f"edit_day_{change_index}"
            )
            
            amount = st.number_input(
                "Amount ($)",
                min_value=0.0,
                step=0.01,
                value=float(data.get("Amount", 0)),
                format="%.2f",
                key=f"edit_amount_{change_index}"
            )
        
        with col2:
            description = st.text_input(
                "Description",
                value=data.get("Description", ""),
                key=f"edit_description_{change_index}"
            )
            
            if data.get("Category") == "Income":
                allocation = st.text_input(
                    "Allocation (Bank/Source)",
                    value=data.get("Allocation", ""),
                    key=f"edit_allocation_{change_index}"
                )
            else:
                category = st.text_input(
                    "Category",
                    value=data.get("Category", ""),
                    key=f"edit_category_{change_index}"
                )
                
                allocation = st.text_input(
                    "Allocation (Income Source)",
                    value=data.get("Allocation", ""),
                    key=f"edit_allocation_{change_index}"
                )
        
        # Checkboxes for flags stacked vertically
        automatic = st.checkbox("⇄ Automatic", value=data.get("Automatic") == "True", key=f"edit_auto_{change_index}")
        paid = st.checkbox("✔ Paid", value=data.get("Paid") == "True", key=f"edit_paid_{change_index}")
        cleared = st.checkbox("✈ Cleared", value=data.get("Cleared") == "True", key=f"edit_cleared_{change_index}")
        
        # Save/Cancel buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("✅ Save", use_container_width=True):
                updated_data = data.copy()
                updated_data["Day"] = int(day)
                updated_data["Amount"] = round(amount, 2)
                updated_data["Description"] = description.strip()
                updated_data["Allocation"] = allocation.strip()
                updated_data["Automatic"] = "True" if automatic else "False"
                updated_data["Paid"] = "True" if paid else "False"
                updated_data["Cleared"] = "True" if cleared else "False"
                
                if data.get("Category") != "Income":
                    updated_data["Category"] = category.strip()
                
                edit_pending_change(change_index, updated_data)
                st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.edited_change_index = None
                # Small delay to allow animation
                import time
                time.sleep(0.15)
                st.rerun()
