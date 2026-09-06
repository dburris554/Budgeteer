"""
Budgeteer CSV Import/Export Handler

Handles CSV upload and download operations with validation and proper integration
with the pending changes workflow.
"""

import streamlit as st
import pandas as pd
from io import StringIO
from typing import Tuple, Optional
from gsheets_manager import BUDGET_COLUMNS, validate_budget_data
from notifications import show_toast, show_success, show_error


def validate_csv_columns(df: pd.DataFrame) -> Tuple[bool, str, list]:
    """
    Validate that CSV has correct columns.
    
    Args:
        df: DataFrame from CSV upload
    
    Returns:
        Tuple of (is_valid: bool, error_message: str, missing_columns: list)
    """
    missing_columns = [col for col in BUDGET_COLUMNS if col not in df.columns]
    
    if missing_columns:
        return False, f"CSV is missing required columns: {', '.join(missing_columns)}", missing_columns
    
    return True, "", []


def parse_csv_file(uploaded_file) -> Tuple[bool, Optional[pd.DataFrame], str]:
    """
    Parse uploaded CSV file.
    
    Args:
        uploaded_file: Streamlit file upload object
    
    Returns:
        Tuple of (success: bool, dataframe: DataFrame or None, message: str)
    """
    try:
        # Read CSV
        df = pd.read_csv(uploaded_file)
        
        # Validate columns
        is_valid, error_msg, _ = validate_csv_columns(df)
        if not is_valid:
            return False, None, f"❌ {error_msg}"
        
        # Validate data
        is_valid, error_msg = validate_budget_data(df)
        if not is_valid:
            return False, None, f"❌ Data validation failed: {error_msg}"
        
        # Ensure correct data types
        try:
            df["Day"] = df["Day"].astype(int)
            df["Amount"] = df["Amount"].astype(float)
        except Exception as e:
            return False, None, f"❌ Data type conversion failed: {str(e)}"
        
        return True, df, f"✅ CSV parsed successfully ({len(df)} entries)"
    
    except pd.errors.ParserError as e:
        return False, None, f"❌ CSV parsing error: {str(e)[:100]}"
    except Exception as e:
        return False, None, f"❌ Error reading CSV: {str(e)[:100]}"


def add_csv_to_pending(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Add all CSV rows as pending changes.
    
    Args:
        df: DataFrame with CSV data
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if "pending_changes" not in st.session_state:
            st.session_state.pending_changes = []
        
        from datetime import datetime
        
        added_count = 0
        for _, row in df.iterrows():
            entry = {
                "Day": int(row["Day"]),
                "Description": str(row["Description"]).strip(),
                "Category": str(row["Category"]).strip(),
                "Amount": float(row["Amount"]),
                "Allocation": str(row["Allocation"]).strip() if "Allocation" in row else " ",
                "Automatic": str(row["Automatic"]).strip() if "Automatic" in row else "False",
                "Paid": str(row["Paid"]).strip() if "Paid" in row else "False",
                "Cleared": str(row["Cleared"]).strip() if "Cleared" in row else "False"
            }
            
            st.session_state.pending_changes.append({
                "type": "add",
                "data": entry,
                "timestamp": datetime.now().isoformat()
            })
            added_count += 1
        
        return True, f"✅ Added {added_count} entries from CSV to pending changes"
    
    except Exception as e:
        return False, f"❌ Error adding CSV entries: {str(e)}"


def export_budget_to_csv() -> Tuple[bool, str, bytes]:
    """
    Export current budget (committed + pending) to CSV format.
    
    Returns:
        Tuple of (success: bool, message: str, csv_bytes: bytes)
    """
    try:
        # Get committed data
        committed_data = st.session_state.get("committed_data", pd.DataFrame())
        
        # Get pending data
        pending_data_list = []
        for change in st.session_state.get("pending_changes", []):
            if change.get("type") == "add":
                pending_data_list.append(change.get("data", {}))
        
        # Combine both
        if not committed_data.empty and pending_data_list:
            pending_df = pd.DataFrame(pending_data_list)
            combined_df = pd.concat([committed_data, pending_df], ignore_index=True)
        elif not committed_data.empty:
            combined_df = committed_data
        elif pending_data_list:
            combined_df = pd.DataFrame(pending_data_list)
        else:
            return False, "❌ No data to export", b""
        
        # Sort by Day
        try:
            combined_df["Day"] = combined_df["Day"].astype(int)
            combined_df = combined_df.sort_values("Day")
        except:
            pass
        
        # Convert to CSV bytes
        csv_string = combined_df.to_csv(index=False)
        csv_bytes = csv_string.encode("utf-8")
        
        return True, f"✅ Export ready ({len(combined_df)} entries)", csv_bytes
    
    except Exception as e:
        return False, f"❌ Export failed: {str(e)}", b""


def render_csv_upload_section() -> None:
    """Render CSV upload section in sidebar."""
    st.sidebar.markdown("### 📤 Import from CSV")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload budget CSV",
        type="csv",
        key="csv_upload",
        help="Upload a CSV file with columns: Day, Description, Category, Amount, Allocation, Automatic, Paid, Cleared"
    )
    
    if uploaded_file is not None:
        # Parse and validate
        success, df, message = parse_csv_file(uploaded_file)
        
        if not success:
            st.sidebar.error(message)
            return
        
        # Show preview
        st.sidebar.success(message)
        
        with st.sidebar.expander("Preview data", expanded=False):
            st.dataframe(df.head(5), use_container_width=True)
        
        # Add button
        if st.sidebar.button("➕ Add to Pending", use_container_width=True, key="add_csv_btn"):
            success, msg = add_csv_to_pending(df)
            if success:
                st.sidebar.success(msg)
                st.rerun()
            else:
                st.sidebar.error(msg)


def render_csv_download_section() -> None:
    """Render CSV download section in sidebar."""
    st.sidebar.markdown("### 📥 Export to CSV")
    
    # Filename input
    current_month = st.session_state.get("current_month", "budget")
    default_filename = f"{current_month.replace('-', '_')}_budget"
    
    filename = st.sidebar.text_input(
        "Filename (without .csv)",
        value=default_filename,
        key="csv_filename",
        help="Name for the exported CSV file"
    )
    
    # Export button
    if st.sidebar.button("📋 Prepare Download", use_container_width=True, key="export_csv_btn"):
        success, message, csv_bytes = export_budget_to_csv()
        
        if not success:
            st.sidebar.error(message)
            return
        
        st.sidebar.success(message)
        
        # Download button
        st.sidebar.download_button(
            label=f"⬇️ Download {filename}.csv",
            data=csv_bytes,
            file_name=f"{filename}.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_csv_btn"
        )
        
        st.toast("✅ CSV exported and ready for download", icon="✅")


def render_csv_section() -> None:
    """Render complete CSV import/export section."""
    render_csv_upload_section()
    st.sidebar.divider()
    render_csv_download_section()


def create_sample_csv() -> bytes:
    """
    Create a sample CSV file for users to understand the format.
    
    Returns:
        CSV content as bytes
    """
    sample_data = {
        "Day": [1, 5, 10, 15, 20],
        "Description": ["Paycheck", "Rent", "Groceries", "Utilities", "Gas"],
        "Category": ["Income", "Housing", "Food", "Utilities", "Transportation"],
        "Amount": [2000.00, 1200.00, 150.00, 100.00, 50.00],
        "Allocation": ["Main Bank", "Main Bank", "Paycheck", "Paycheck", "Paycheck"],
        "Automatic": ["False", "True", "False", "True", "False"],
        "Paid": ["False", "True", "True", "True", "False"],
        "Cleared": ["True", "False", "False", "False", "False"]
    }
    
    df = pd.DataFrame(sample_data)
    csv_string = df.to_csv(index=False)
    return csv_string.encode("utf-8")
