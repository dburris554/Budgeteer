"""
Budgeteer Trash Management

Handles deletion and restoration of pending changes and committed entries.
"""

import streamlit as st
from typing import Dict, Any, List
from datetime import datetime


def initialize_trash() -> None:
    """Initialize trash in session state."""
    if "trash" not in st.session_state:
        st.session_state.trash = []


def trash_item(item: Dict[str, Any], item_type: str = "pending") -> None:
    """
    Move an item to trash.
    
    Args:
        item: Item to trash (pending change or committed entry)
        item_type: "pending" or "committed"
    """
    if "trash" not in st.session_state:
        st.session_state.trash = []
    
    st.session_state.trash.append({
        "item": item,
        "type": item_type,
        "timestamp": datetime.now().isoformat()
    })


def restore_item(trash_index: int) -> bool:
    """
    Restore an item from trash.
    
    Args:
        trash_index: Index of item in trash
    
    Returns:
        True if restore successful
    """
    if trash_index < 0 or trash_index >= len(st.session_state.get("trash", [])):
        return False
    
    trashed = st.session_state.trash.pop(trash_index)
    item = trashed["item"]
    item_type = trashed["type"]
    
    if item_type == "pending":
        # Restore to pending changes
        if "pending_changes" not in st.session_state:
            st.session_state.pending_changes = []
        st.session_state.pending_changes.append(item)
    elif item_type == "committed":
        # Restore to committed data
        import pandas as pd
        if st.session_state.committed_data.empty:
            st.session_state.committed_data = pd.DataFrame([item])
        else:
            st.session_state.committed_data = pd.concat(
                [st.session_state.committed_data, pd.DataFrame([item])],
                ignore_index=True
            )
    
    return True


def empty_trash() -> None:
    """Permanently delete all items in trash."""
    st.session_state.trash = []


def get_trash_count() -> int:
    """Get number of items in trash."""
    return len(st.session_state.get("trash", []))


def format_trash_item_display(trash_item: Dict[str, Any]) -> str:
    """
    Format a trash item for display.
    
    Args:
        trash_item: Item from trash with 'item', 'type', 'timestamp'
    
    Returns:
        Formatted string for display
    """
    item = trash_item.get("item", {})
    item_type = trash_item.get("type", "unknown")
    
    # Handle pending changes (which have 'data' key)
    if isinstance(item, dict) and "data" in item:
        data = item.get("data", {})
        description = data.get("Description", "Unknown")
        amount = data.get("Amount", 0)
        day = data.get("Day", "-")
        category = data.get("Category", "")
        
        if category == "Income":
            return f"🗑️ Income: {description} - ${amount:,.2f} on day {day}"
        else:
            return f"🗑️ Expense: {description} ({category}) - ${amount:,.2f} on day {day}"
    
    # Handle committed entries (which are pandas Series as dict)
    elif isinstance(item, dict):
        description = item.get("Description", "Unknown")
        amount = item.get("Amount", 0)
        day = item.get("Day", "-")
        category = item.get("Category", "")
        
        if category == "Income":
            return f"🗑️ Income: {description} - ${float(amount):,.2f} on day {day}"
        else:
            return f"🗑️ Expense: {description} ({category}) - ${float(amount):,.2f} on day {day}"
    
    return "🗑️ Deleted item"


def render_trash_section() -> None:
    """Render trash/recycle bin section."""
    initialize_trash()
    
    trash = st.session_state.get("trash", [])
    trash_count = len(trash)
    
    if trash_count == 0:
        st.info("🗑️ Trash is empty. Deleted items appear here.", icon="ℹ️")
        return
    
    with st.expander(f"🗑️ Trash ({trash_count} item{'s' if trash_count != 1 else ''})", expanded=False):
        # Display trash items
        for idx, trashed in enumerate(trash):
            col1, col2, col3 = st.columns([4, 0.5, 0.5], gap="small")
            
            with col1:
                display_text = format_trash_item_display(trashed)
                st.text(display_text)
            
            with col2:
                if st.button("↩️", key=f"restore_{idx}"):
                    if restore_item(idx):
                        st.toast("✅ Item restored", icon="✅")
                        st.rerun()
            
            with col3:
                if st.button("❌", key=f"delete_permanently_{idx}"):
                    st.session_state.trash.pop(idx)
                    st.toast("🗑️ Item permanently deleted", icon="✅")
                    st.rerun()
        
        st.divider()
        
        # Empty trash button
        if st.button("🗑️ Empty Trash", use_container_width=True):
            empty_trash()
            st.toast("✅ Trash emptied", icon="✅")
            st.rerun()
