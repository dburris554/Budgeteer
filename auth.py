"""
Budgeteer Authentication Module

Handles authentication using Streamlit-Authenticator with support for:
- Single-user password authentication
- Temporary session mode (guest access)
- Logout and session switching
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path


def load_auth_config(config_path: str = "auth_config.yaml") -> dict:
    """Load authentication configuration from YAML file."""
    try:
        with open(config_path) as file:
            config = yaml.load(file, Loader=SafeLoader)
        return config
    except FileNotFoundError:
        st.error(f"Authentication config file not found: {config_path}")
        st.info("Please ensure auth_config.yaml exists in the project root.")
        st.stop()


def save_auth_config(config: dict, config_path: str = "auth_config.yaml") -> None:
    """Save authentication configuration to YAML file."""
    try:
        with open(config_path, "w") as file:
            yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        st.error(f"Failed to save auth config: {e}")


def initialize_authenticator() -> stauth.Authenticate:
    """Initialize Streamlit Authenticator with config."""
    config = load_auth_config()
    
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        auto_hash=True,  # Automatically hash passwords
    )
    
    return authenticator, config


def render_auth_page(authenticator: stauth.Authenticate) -> bool:
    """
    Render authentication page with login and guest access options.
    
    Returns:
        True if user authenticated or chose guest mode, False otherwise
    """
    st.set_page_config(
        page_title="Budgeteer Login",
        page_icon="🚀",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.header("Budgeteer", anchor=False)
        st.subheader("Personal Budget Planner", anchor=False)
        st.divider()
    
    tab1, tab2 = st.tabs(["Login", "Guest Access"])
    
    with tab1:
        st.write("**Sign in with your credentials to access saved budgets via Google Sheets.**")
        try:
            authenticator.login(location="main", fields={"Form name": "Login to Budgeteer"})
        except Exception as e:
            st.error(f"Login error: {e}")
    
    with tab2:
        st.write("""
        **Use Budgeteer without an account.**
        
        Your budget data will be stored in your browser session only and will be lost 
        when you close the browser or navigate away. Perfect for quick budget planning 
        or testing the app.
        """)
        
        if st.button("Continue as Guest", use_container_width=True, type="primary"):
            st.session_state["authentication_status"] = None  # Guest mode indicator
            st.session_state["auth_mode"] = "temp"
            st.rerun()
    
    # Check authentication status
    if st.session_state.get("authentication_status"):
        st.success("✅ Login successful! Redirecting...")
        st.session_state["auth_mode"] = "authenticated"
        st.session_state["gsheets_connection_required"] = True
        return True
    elif st.session_state.get("authentication_status") is False:
        st.error("❌ Username or password is incorrect. Please try again.")
    elif st.session_state.get("auth_mode") == "temp":
        return True  # Guest mode selected
    
    return False


def check_authentication() -> bool:
    """
    Check if user is authenticated or in guest mode.
    
    Returns:
        True if user can access the app, False otherwise
    """
    auth_status = st.session_state.get("authentication_status")
    auth_mode = st.session_state.get("auth_mode")
    
    # User is authenticated or in guest mode
    if auth_status or auth_mode == "temp":
        return True
    
    # Not authenticated and not in guest mode
    return False


def render_logout_button(authenticator: stauth.Authenticate, config: dict) -> None:
    """
    Render logout button in sidebar.
    Updates auth config after logout to persist state changes.
    """
    try:
        authenticator.logout(location="sidebar", button_name="🚪 Logout")
        
        # Save config after logout to persist authentication state changes
        if not st.session_state.get("authentication_status"):
            save_auth_config(config)
            st.session_state["auth_mode"] = None
    except Exception as e:
        st.sidebar.error(f"Logout error: {e}")


def get_current_user() -> str:
    """Get the username of the currently authenticated user."""
    if st.session_state.get("authentication_status"):
        return st.session_state.get("username", "Unknown User")
    else:
        return "Guest User"


def get_auth_mode() -> str:
    """Get current authentication mode ('authenticated' or 'temp')."""
    return st.session_state.get("auth_mode", "unknown")


def is_authenticated() -> bool:
    """Check if user is authenticated (not in guest/temp mode)."""
    return st.session_state.get("authentication_status") is True
