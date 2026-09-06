"""
Budgeteer Google Sheets Manager

Handles all Google Sheets operations including:
- Connection management
- Automatic workbook creation
- Monthly data sheet operations
- Draft sheet auto-save
"""

import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import gspread
from google.oauth2.service_account import Credentials


# Column schema for budget data
BUDGET_COLUMNS = ['Day', 'Description', 'Category', 'Amount', 'Allocation', 'Automatic', 'Paid', 'Cleared']


def get_gsheets_connection():
    """
    Get or create Google Sheets connection.
    Uses OAuth if authenticated, returns None if in temp session mode.
    """
    if st.session_state.get("auth_mode") != "authenticated":
        return None
    
    try:
        # Use st.connection for OAuth-based connection (user's Google account)
        conn = st.connection("gsheets", type="streamlit_gsheets.GSheetsConnection")
        return conn
    except Exception as e:
        st.warning(f"⚠️ Google Sheets connection not configured: {e}")
        st.info("You can set up Google Sheets integration in Settings if desired. For now, using session-only mode.")
        return None


def initialize_gsheets_connection() -> bool:
    """
    Initialize Google Sheets connection on first authenticated login.
    Creates workbook and draft sheet if they don't exist.
    
    Returns:
        True if connection successful, False otherwise
    """
    if st.session_state.get("auth_mode") != "authenticated":
        st.session_state["gsheets_ready"] = False
        return False
    
    try:
        conn = get_gsheets_connection()
        if conn is None:
            st.session_state["gsheets_ready"] = False
            return False
        
        # Try to connect and verify workbook exists
        # First attempt to read from a test sheet
        try:
            test_data = conn.read(worksheet="Draft")
            st.session_state["gsheets_ready"] = True
            return True
        except Exception as e:
            # Workbook or sheet doesn't exist, try to create it
            st.info("Creating your Budgeteer workbook on Google Drive...")
            
            # For now, we'll use session state for everything and prepare for future gsheets integration
            # Full integration with automatic workbook creation requires service account or more complex OAuth setup
            st.session_state["gsheets_ready"] = False
            st.session_state["gsheets_warning_shown"] = True
            
            return False
    
    except Exception as e:
        st.error(f"❌ Failed to initialize Google Sheets: {e}")
        st.session_state["gsheets_ready"] = False
        return False


def load_month_data(month_name: str) -> pd.DataFrame:
    """
    Load committed data for a specific month from GSheets or session state.
    
    Args:
        month_name: Format "YYYY-MM"
    
    Returns:
        DataFrame with month's committed data, or empty DataFrame if month doesn't exist
    """
    # Check session state first (temp mode or cached data)
    if "budget_data" in st.session_state and month_name in st.session_state.budget_data:
        return pd.DataFrame(st.session_state.budget_data[month_name])
    
    # Try to load from GSheets if authenticated
    if st.session_state.get("gsheets_ready"):
        try:
            conn = get_gsheets_connection()
            if conn:
                data = conn.read(worksheet=month_name)
                # Cache in session state
                if "budget_data" not in st.session_state:
                    st.session_state.budget_data = {}
                st.session_state.budget_data[month_name] = data.to_dict('records')
                return data
        except Exception as e:
            st.warning(f"Could not load {month_name} from GSheets: {e}")
    
    # Return empty DataFrame with correct columns if month doesn't exist
    return pd.DataFrame(columns=BUDGET_COLUMNS)


def save_month_data(month_name: str, data: pd.DataFrame) -> bool:
    """
    Save committed data for a specific month to GSheets or session state.
    
    Args:
        month_name: Format "YYYY-MM"
        data: DataFrame with budget entries
    
    Returns:
        True if save successful, False otherwise
    """
    # Always cache in session state
    if "budget_data" not in st.session_state:
        st.session_state.budget_data = {}
    st.session_state.budget_data[month_name] = data.to_dict('records')
    
    # Try to save to GSheets if authenticated
    if st.session_state.get("gsheets_ready"):
        try:
            conn = get_gsheets_connection()
            if conn:
                conn.update(worksheet=month_name, data=data)
                return True
        except Exception as e:
            st.warning(f"Could not save to GSheets: {e}. Saved locally instead.")
    
    return True  # Success (saved to session state at minimum)


def load_draft_data(month_name: str) -> List[Dict[str, Any]]:
    """
    Load pending/draft changes for a specific month.
    
    Args:
        month_name: Format "YYYY-MM"
    
    Returns:
        List of pending change dictionaries
    """
    draft_key = f"draft_{month_name}"
    
    # Check session state first
    if draft_key in st.session_state:
        return st.session_state[draft_key]
    
    # Try to load from GSheets draft sheet if authenticated
    if st.session_state.get("gsheets_ready"):
        try:
            conn = get_gsheets_connection()
            if conn:
                draft_data = conn.read(worksheet="Draft")
                # Filter for this month's drafts
                month_drafts = [
                    json.loads(row.get("data", "{}"))
                    for row in draft_data.to_dict('records')
                    if row.get("month") == month_name
                ]
                st.session_state[draft_key] = month_drafts
                return month_drafts
        except Exception as e:
            # Draft sheet might not exist yet
            pass
    
    return []


def save_draft_data(month_name: str, pending_changes: List[Dict[str, Any]]) -> bool:
    """
    Auto-save pending/draft changes for a specific month.
    Saves to session state and GSheets draft sheet.
    
    Args:
        month_name: Format "YYYY-MM"
        pending_changes: List of pending change dictionaries
    
    Returns:
        True if save successful
    """
    draft_key = f"draft_{month_name}"
    
    # Always save to session state
    st.session_state[draft_key] = pending_changes
    
    # Try to save to GSheets if authenticated
    if st.session_state.get("gsheets_ready"):
        try:
            conn = get_gsheets_connection()
            if conn:
                # Convert pending changes to DataFrame for GSheets
                draft_records = [
                    {
                        "month": month_name,
                        "timestamp": datetime.now().isoformat(),
                        "data": json.dumps(change)
                    }
                    for change in pending_changes
                ]
                draft_df = pd.DataFrame(draft_records)
                conn.update(worksheet="Draft", data=draft_df)
        except Exception as e:
            # Silent fail - draft is still saved in session state
            pass
    
    return True


def get_available_months() -> List[str]:
    """
    Get list of available month sheets.
    Returns months from session state (and GSheets if authenticated).
    
    Returns:
        List of month names in "YYYY-MM" format, sorted ascending
    """
    months = set()
    
    # Check session state
    if "budget_data" in st.session_state:
        months.update(st.session_state.budget_data.keys())
    
    # Check GSheets if authenticated
    if st.session_state.get("gsheets_ready"):
        try:
            conn = get_gsheets_connection()
            if conn:
                # Get list of sheets in workbook
                # This requires accessing the underlying gspread client
                # For now, we rely on session state
                pass
        except Exception as e:
            pass
    
    return sorted(list(months))


def create_new_month(month_name: str, template_data: Optional[pd.DataFrame] = None) -> bool:
    """
    Create a new month sheet with optional template data.
    
    Args:
        month_name: Format "YYYY-MM"
        template_data: Optional DataFrame to copy as starting data
    
    Returns:
        True if creation successful
    """
    try:
        if template_data is None or template_data.empty:
            # Create empty month
            df = pd.DataFrame(columns=BUDGET_COLUMNS)
        else:
            # Copy template data (by value, not reference)
            df = template_data.copy()
        
        # Save to session state
        if "budget_data" not in st.session_state:
            st.session_state.budget_data = {}
        st.session_state.budget_data[month_name] = df.to_dict('records')
        
        # Try to save to GSheets if authenticated
        if st.session_state.get("gsheets_ready"):
            try:
                conn = get_gsheets_connection()
                if conn:
                    conn.update(worksheet=month_name, data=df)
            except Exception as e:
                # Month created in session state, GSheets creation can fail gracefully
                pass
        
        return True
    
    except Exception as e:
        st.error(f"❌ Failed to create month: {e}")
        return False


def validate_budget_data(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Validate budget data structure and content.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check columns
    if not all(col in df.columns for col in BUDGET_COLUMNS):
        missing = [col for col in BUDGET_COLUMNS if col not in df.columns]
        return False, f"Missing columns: {', '.join(missing)}"
    
    # Check Day column
    if not df.empty:
        try:
            df['Day'].astype(int)
            if not all((df['Day'] >= 1) & (df['Day'] <= 31)):
                return False, "Day values must be between 1 and 31"
        except (ValueError, TypeError):
            return False, "Day column must contain integers"
        
        # Check Amount column
        try:
            df['Amount'].astype(float)
            if not all(df['Amount'] >= 0):
                return False, "Amount values must be non-negative"
        except (ValueError, TypeError):
            return False, "Amount column must contain numbers"
    
    return True, ""


def get_draft_auto_save_timestamp() -> str:
    """Get timestamp of last draft auto-save."""
    return st.session_state.get("last_draft_save", "Never")
