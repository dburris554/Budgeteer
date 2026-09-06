import streamlit as st
from pandas import DataFrame
import pandas as pd
from enum import Enum
import plotly.graph_objects as go
import altair as alt
import numpy as np
# TODO: Remove these legacy imports - will be replaced in Task 5
# import friendlywords as fw
# from st_aggrid import GridOptionsBuilder, ColumnsAutoSizeMode, AgGridTheme, JsCode, AgGrid
from streamlit.components.v1 import html

# Import authentication module
from auth import initialize_authenticator, render_auth_page, check_authentication, render_logout_button, is_authenticated
from gsheets_manager import initialize_gsheets_connection
from month_manager import initialize_month_state, render_month_selector, switch_month, handle_month_creation, render_month_summary_metrics
from data_entry import render_data_entry_section, render_committed_data_table
from pending_changes import initialize_pending_changes, render_pending_changes_section, get_pending_changes_count
from commit import render_save_section, auto_save_draft
from csv_handler import render_csv_section
from notifications import show_success, show_error, show_warning, show_info
from insights import render_insights_tab

# Layout changes
st.set_page_config(page_title='Budgeteer', page_icon='🚀', layout="wide", initial_sidebar_state='expanded')

# Hide "Press Enter to Submit Form" text from form inputs and reduce heading sizes
st.markdown("""
<style>
    .stTextInput > div > div > span,
    .stNumberInput > div > div > span {
        display: none !important;
    }
    h1 {
        font-size: 1.5rem !important;
        margin-bottom: 0.3rem !important;
    }
    h2 {
        font-size: 1.2rem !important;
        margin-bottom: 0.3rem !important;
    }
    h3 {
        font-size: 1rem !important;
        margin-bottom: 0.2rem !important;
    }
    h4, h5, h6 {
        font-size: 0.95rem !important;
        margin-bottom: 0.2rem !important;
    }
    .stMarkdown {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    hr {
        margin-top: 0.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Freeze tabs at top */
    [data-testid="stTabs"] {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: white;
    }
    
    /* Edit dialog animation */
    [data-testid="stForm"] {
        animation: slideDown 0.3s ease-out;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize authentication
if "authenticator" not in st.session_state:
    authenticator, auth_config = initialize_authenticator()
    st.session_state.authenticator = authenticator
    st.session_state.auth_config = auth_config
else:
    authenticator = st.session_state.authenticator
    auth_config = st.session_state.auth_config

# Check if user needs to authenticate
if not check_authentication():
    if render_auth_page(authenticator):
        # Show success toast on first auth
        if st.session_state.get("authentication_status"):
            show_success("✅ Welcome! You're logged in.", duration="short")
        st.rerun()
    else:
        st.stop()

# User is authenticated or in guest mode - render logout button
if st.session_state.get("authentication_status"):
    render_logout_button(authenticator, auth_config)
    # Update auth config after logout
    if not st.session_state.get("authentication_status"):
        show_info("👋 You've been logged out.", duration="short")
        st.rerun()

# Initialize GSheets connection if authenticated
if is_authenticated() and "gsheets_ready" not in st.session_state:
    initialize_gsheets_connection()

# Initialize month and budget state
initialize_month_state()

# Initialize pending changes
# Initialize pending changes
initialize_pending_changes()

# Note: Custom CSS for hiding menu has been removed.
# Modern Streamlit handles this natively through configuration.
# See .streamlit/config.toml for theme settings.

# Constants
SAMPLE_COLS = ('Day', 'Description', 'Category', 'Amount', 'Allocation', 'Automatic', 'Paid', 'Cleared')
SAMPLE_ROWS = [(1, 'Paycheck 1', 'Income', 2000.59, 'ABC Bank', 'True', 'False', 'True'),
          (2, 'Rent', 'Housing', 1000, 'Paycheck 1', 'False', 'True', 'True'),
          (2, 'Electric', 'Housing', 205.42, 'Paycheck 1', 'False', 'False', 'False'),
          (7, 'Paycheck 2', 'Income', 500, 'Ameri-bank', 'True', 'False', 'False'),
          (12, 'Doctor appt.', 'Medical', 60, 'Paycheck 2', 'False', 'False', 'False'),
          (14, 'Car payment', 'Loans', 300, 'Paycheck 1', 'True', 'False', 'False'),
          (15, 'Walmart', 'Groceries', 150, 'Paycheck 2', 'False', 'False', 'False')]
SAMPLE = pd.DataFrame([dict(zip(SAMPLE_COLS, SAMPLE_ROWS[i])) for i in range(len(SAMPLE_ROWS))])
HEIGHT = 500

class DataFrameMutateMode(Enum):
    APPEND = 1
    PREPEND = 2
    REMOVE = 3
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented

# Global data
stable = pd.DataFrame(columns=SAMPLE_COLS) # initial loaded data or updated data to be the source of truth
modified = pd.DataFrame() # data post-AgGrid modifications
selected = None # rows selected from AgGrid
if 'dataframe' in st.session_state:
    stable = pd.DataFrame(st.session_state.dataframe)
else:
    st.session_state.dataframe = stable
if 'csv' not in st.session_state:
   st.session_state.csv = ''
# TODO: Remove friendlywords usage in Task 5 - forms will start empty
# fw.preload() # type: ignore
# sample_values = dict(zip(SAMPLE_COLS, [0, fw.generate(3), fw.generate(1), 0.0, ' ', 'False', 'False', 'False'])) # type: ignore
sample_values = dict(zip(SAMPLE_COLS, [0, 'Sample Description', 'Category', 0.0, ' ', 'False', 'False', 'False']))
new_row = pd.DataFrame([[sample_values[col] if col in sample_values.keys() else ' ' for col in stable.columns]], columns=stable.columns) # type: ignore
# TODO: Remove ColumnsAutoSizeMode in Task 5 - AgGrid will be removed
column_size_mode = 'FIT_CONTENTS'  # ColumnsAutoSizeMode.FIT_CONTENTS
if 'size_mode' in st.session_state:
    column_size_mode = st.session_state.size_mode
else:
    st.session_state.size_mode = column_size_mode

# Callback Functions (DEPRECATED - kept for reference only)
# These functions were used with AgGrid for inline data editing.
# They are no longer used as Budgeteer now uses form-based data entry.
# Kept here for potential backwards compatibility or legacy code reference.

def load_empty():
    # DEPRECATED: Use month creation dialog instead
    global stable
    stable = pd.DataFrame(columns=SAMPLE_COLS)
    st.session_state.size_mode = 'FIT_CONTENTS'

def load_sample():
    # DEPRECATED: Manual data entry is preferred
    global stable
    stable = SAMPLE
    st.session_state.dataframe = stable

def mutate(rows: DataFrame, mode: DataFrameMutateMode):
    # DEPRECATED: Use pending_changes workflow instead
    global modified
    rows['Day'] = rows['Day'].astype(int)
    rows['Amount'] = rows['Amount'].astype(float)
    if modified.empty:
        global stable
        if stable.empty:
            rows['Automatic'] = rows['Automatic'].astype(str)
            rows['Paid'] = rows['Paid'].astype(str)
            rows['Cleared'] = rows['Cleared'].astype(str)
        if mode == DataFrameMutateMode.APPEND:
            stable = pd.concat([stable, rows])
        elif mode == DataFrameMutateMode.PREPEND:
            stable = pd.concat([rows, stable])
        elif mode == DataFrameMutateMode.REMOVE:
            stable = pd.merge(stable, rows, how='outer', indicator=True).query("_merge != 'both'").drop('_merge', axis=1).reset_index(drop=True)
        st.session_state.dataframe = stable
    else:
        modified['Day'] = modified['Day'].astype(int)
        modified['Amount'] = modified['Amount'].astype(float)
        if mode == DataFrameMutateMode.APPEND:
            st.session_state.dataframe = pd.concat([modified, rows])
        elif mode == DataFrameMutateMode.PREPEND:
            st.session_state.dataframe = pd.concat([rows, modified])
        elif mode == DataFrameMutateMode.REMOVE:
            st.session_state.dataframe = pd.merge(modified, rows, how='outer', indicator=True).query("_merge != 'both' & _merge != 'right_only'").drop('_merge', axis=1).reset_index(drop=True)

def convert_to_csv():
    # DEPRECATED: Use csv_handler.export_budget_to_csv() instead
    global modified
    global stable
    if not modified.empty:
        stable = modified
    stable['Day'] = stable['Day'].astype(int)
    st.session_state.csv = stable.sort_values('Day').to_csv(index=False).encode('utf-8')

def switch_size_mode():
    # DEPRECATED: No longer used with form-based UI
    global column_size_mode
    global stable
    if column_size_mode == 'FIT_CONTENTS':
        column_size_mode = 'FIT_ALL_COLUMNS_TO_VIEW'
    elif column_size_mode == 'FIT_ALL_COLUMNS_TO_VIEW':
        column_size_mode = 'FIT_CONTENTS'
    st.session_state.size_mode = column_size_mode
    st.session_state.dataframe = stable

def cb_renderer():
    # TODO: Remove in final cleanup - was used for AgGrid checkbox rendering
    # Native Streamlit components now handle this
    pass

def income_checker():
    # TODO: Remove in final cleanup - was used for AgGrid custom rendering
    # Native Streamlit components with column_config now handle this
    pass

def row_coloring():
    # TODO: Remove in final cleanup - was used for AgGrid row styling
    # Modern Streamlit themes handle styling
    pass

# Streamlit componenets
st.subheader('Welcome, fellow Budgeteer! :wave:')
data_tab, insights_tab, about_tab, donate_tab = st.tabs(['Data', 'Insights', 'About', 'Donate'])

with st.sidebar:
    # Render month selector
    selected_month = render_month_selector()
    
    # Handle month switching
    if selected_month != st.session_state.get("current_month"):
        switch_month(selected_month)
        st.rerun()
    
    # Handle new month creation dialog
    handle_month_creation()
    
    st.divider()
    
    # Render CSV import/export section
    render_csv_section()

with data_tab:
    # Display month summary metrics
    st.markdown(f"##### 📊 {st.session_state.get('current_month', 'Current Month')} Summary")
    render_month_summary_metrics()
    st.divider()
    
    # Render data entry forms
    render_data_entry_section()
    st.divider()
    
    # Render pending changes section
    render_pending_changes_section()
    
    st.divider()
    
    # Render save & commit section
    render_save_section()
    
    st.divider()
    
    # Render committed data table
    st.markdown("##### 📋 Committed Entries")
    render_committed_data_table()
    
    st.divider()
    
    # Render trash section
    from trash import render_trash_section
    render_trash_section()
    
    # Auto-save draft on every rerun
    auto_save_draft()

with insights_tab:
    render_insights_tab()

with about_tab:
    st.markdown("#### 📚 About Budgeteer")
    st.markdown("##### Version 1.0.0")
    
    # Quick overview
    st.markdown("""
    Budgeteer is a personal budget planning application that helps you organize your income, 
    track expenses, and understand your financial flow throughout the month.
    """)
    
    # Feature highlights
    with st.expander("✨ **Features**", expanded=True):
        st.markdown("""
        - **📝 Form-Based Data Entry** - Structured forms for adding income and expenses
        - **📅 Monthly Budget Organization** - Create separate budgets for each month
        - **⏳ Staged Changes Workflow** - Review changes before committing to prevent errors
        - **💾 Optional Google Sheets Integration** - Cloud backup and persistent storage
        - **🔐 Single-User Authentication** - Secure password protection
        - **📊 Interactive Visualizations** - Charts and graphs to understand your budget
        - **💾 Draft Auto-Save** - Automatic backup of uncommitted changes
        - **📥 CSV Import/Export** - Import existing budgets or export for external analysis
        - **👤 Guest Mode** - Try the app without authentication (session-only)
        """)
    
    # Getting started
    with st.expander("🚀 **Getting Started**", expanded=False):
        st.markdown("""
        1. **Choose Your Access Mode**
           - Login for persistent storage with Google Sheets
           - Or continue as guest for session-only mode
        
        2. **Create or Select a Month**
           - Use the "📅 Monthly Budget" selector in the sidebar
           - Click "➕ New Month" to create a new budget
        
        3. **Add Entries**
           - Click "➕ Add Income" or "➕ Add Expense"
           - Fill out the form and submit
           - Entries appear in the Pending Changes section
        
        4. **Review and Commit**
           - Check pending changes
           - Click "✅ Commit & Save"
           - Entries now part of your committed budget
        
        5. **Explore Insights**
           - Switch to Insights tab
           - View visualizations of your budget
        """)
    
    # Data entry guide
    with st.expander("✏️ **Data Entry Guide**", expanded=False):
        st.markdown("""
        ### Income Form
        - **Day**: What day will this income arrive? (1-31)
        - **Description**: Name of income (e.g., "Paycheck")
        - **Amount**: Income amount in dollars
        - **Allocation**: Bank or source (e.g., "Chase")
        - **Cleared**: Is this income cleared?
        
        ### Expense Form
        - **Day**: When will expense occur? (1-31)
        - **Description**: Name of expense (e.g., "Rent")
        - **Category**: Type (e.g., "Housing", "Food")
        - **Amount**: Expense amount in dollars
        - **Paid from**: Which income covers this expense
        - **Automatic**: Automatically deducted?
        - **Paid**: Has this been paid?
        - **Cleared**: Has this cleared the account?
        """)
    
    # Workflow explanation
    with st.expander("⚙️ **How the Workflow Works**", expanded=False):
        st.markdown("""
        ### Pending Changes
        When you add entries, they're staged in "Pending Changes" for review.
        
        **Benefits:**
        - Catch errors before saving
        - Review all changes at once
        - Edit or delete before committing
        - See clear before/after state
        
        ### Committing
        Click "✅ Commit & Save" to make pending changes permanent.
        
        **What Happens:**
        - All pending changes applied to committed budget
        - Data saved to local storage and Google Sheets (if connected)
        - Pending list cleared
        - Committed entries appear below
        
        ### Draft Auto-Save
        Your pending changes are automatically backed up:
        - Saved to Draft sheet (if Google Sheets connected)
        - Protection against connection loss or crashes
        - Survives browser close (even without committing)
        """)
    
    # Insights explanation
    with st.expander("📊 **Understanding Insights**", expanded=False):
        st.markdown("""
        ### Summary Metrics
        - **Total Income**: All income combined
        - **Total Expenses**: All expenses combined
        - **Net Balance**: Income minus Expenses
        
        ### Visualizations
        - **Pending Charges**: Automatic/Paid expenses not yet cleared
        - **Unpaid Charges**: Expenses you haven't paid yet
        - **Income Burndowns**: How balance changes throughout the month
        - **Data Exploration**: Income distribution and flow charts
        
        **Tip:** Burndown charts show when you might run out of money from each income source.
        """)
    
    # CSV guide
    with st.expander("📥 **CSV Import/Export**", expanded=False):
        st.markdown("""
        ### Importing CSV
        1. Click "📤 Import from CSV" in sidebar
        2. Upload a CSV file with columns:
           - Day, Description, Category, Amount, Allocation, Automatic, Paid, Cleared
        3. Preview the data
        4. Click "➕ Add to Pending" to import
        5. Review and commit as normal
        
        ### Exporting CSV
        1. Click "📥 Export to CSV" in sidebar
        2. Enter filename (optional)
        3. Click "📋 Prepare Download"
        4. Click download button
        
        **Exported data includes:** All committed entries + all pending entries
        """)
    
    # Google Sheets guide
    with st.expander("☁️ **Google Sheets Integration (Optional)**", expanded=False):
        st.markdown("""
        ### What It Does
        - Automatic backup of your budget
        - Access from multiple devices
        - Permanent cloud storage
        
        ### How to Set Up
        1. Log in with your credentials
        2. Budgeteer will ask for Google authorization
        3. Authorize access to your Google account
        4. Connection established!
        
        ### Data Structure
        - Workbook: "Budgeteer_Budget"
        - One sheet per month (e.g., "2024-01")
        - "Draft" sheet for backup of pending changes
        
        ### If Connection Fails
        - Budgeteer continues working in local-only mode
        - Export to CSV to backup your data
        - Try logging in again or use guest mode
        """)
    
    # Tips and best practices
    with st.expander("💡 **Tips & Best Practices**", expanded=False):
        st.markdown("""
        ### Organization
        - Use consistent category names (Housing, Food, etc.)
        - Use recognizable allocation names (Main Bank, Paycheck, etc.)
        - Mark Paid/Cleared to track payment status
        
        ### Workflow
        - Add all income entries first (for allocation dropdown)
        - Batch add entries, then commit once
        - Use edit/delete liberally before committing
        - Check insights weekly to spot spending patterns
        
        ### Analysis
        - Burndown charts: flat = good, dropping = spending faster
        - Pending vs Unpaid: focus on unpaid to see what's due
        - Net Balance: positive = surplus, negative = overspending
        """)
    
    # Troubleshooting
    with st.expander("🔧 **Troubleshooting**", expanded=False):
        st.markdown("""
        ### Login Issues
        - Check username/password (case-sensitive)
        - Look for Caps Lock
        
        ### No Data in Insights
        - You need to commit entries first (they're pending)
        - Add entries using forms and click "✅ Commit & Save"
        
        ### CSV Import Errors
        - Check all required columns present
        - Verify Day is 1-31
        - Verify Amount is numeric (no $ signs)
        
        ### Lost Data (Guest Mode)
        - Guest mode data doesn't persist
        - Use authenticated mode with Google Sheets for persistence
        
        ### Contact Support
        - Check this About tab for answers
        - Read DOCUMENTATION.md for detailed guide
        """)
    
    st.divider()
    st.caption("📖 For detailed documentation, see DOCUMENTATION.md in the project repository")

with donate_tab:
    st.markdown("#### ☕ Support Budgeteer")
    st.markdown("""
    If you find Budgeteer helpful and would like to support continued development, 
    consider buying me a coffee!
    """)
    
    st.markdown("""
    <div style="text-align: center; margin: 1rem 0;">
        <a href="https://buymeacoffee.com/burris" target="_blank" style="
            display: inline-block;
            background-color: #5F7FFF;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            text-decoration: none;
            font-weight: bold;
            font-size: 1rem;
        ">☕ Buy me a coffee</a>
    </div>
    """, unsafe_allow_html=True)

# Debugging
# st.write("Session State", st.session_state)
