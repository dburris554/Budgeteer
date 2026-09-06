"""
Budgeteer Toast Notifications

Centralized toast notification system for all key actions.
"""

import streamlit as st


# Notification types with default settings
NOTIFICATIONS = {
    # Authentication
    "auth_login_success": {
        "message": "✅ Welcome back! You're logged in.",
        "icon": "✅",
        "duration": "short"
    },
    "auth_login_failed": {
        "message": "❌ Login failed. Check your credentials and try again.",
        "icon": "❌",
        "duration": "long"
    },
    "auth_logout": {
        "message": "👋 You've been logged out. See you next time!",
        "icon": "👋",
        "duration": "short"
    },
    "auth_guest_mode": {
        "message": "👤 Continuing as guest. Your data will be saved in this session only.",
        "icon": "ℹ️",
        "duration": "long"
    },
    
    # GSheets operations
    "gsheets_connected": {
        "message": "☁️ Connected to Google Sheets!",
        "icon": "☁️",
        "duration": "short"
    },
    "gsheets_connection_failed": {
        "message": "⚠️ Could not connect to Google Sheets. Using session storage.",
        "icon": "⚠️",
        "duration": "long"
    },
    "gsheets_data_loaded": {
        "message": "📥 Data loaded from Google Sheets",
        "icon": "📥",
        "duration": "short"
    },
    "gsheets_data_saved": {
        "message": "☁️ Data saved to Google Sheets",
        "icon": "☁️",
        "duration": "short"
    },
    
    # Data entry
    "entry_added": {
        "message": "✅ Entry added to pending changes",
        "icon": "✅",
        "duration": "short"
    },
    "entry_validation_error": {
        "message": "❌ Please check your entry and try again",
        "icon": "❌",
        "duration": "long"
    },
    "entry_required_field": {
        "message": "⚠️ Please fill in all required fields",
        "icon": "⚠️",
        "duration": "short"
    },
    
    # Pending changes
    "change_edited": {
        "message": "✏️ Change updated",
        "icon": "✏️",
        "duration": "short"
    },
    "change_deleted": {
        "message": "🗑️ Change removed",
        "icon": "🗑️",
        "duration": "short"
    },
    "pending_cleared": {
        "message": "✨ All pending changes cleared",
        "icon": "✨",
        "duration": "short"
    },
    
    # Commit operations
    "commit_success": {
        "message": "✅ Changes committed successfully!",
        "icon": "✅",
        "duration": "short"
    },
    "commit_failed": {
        "message": "❌ Failed to commit changes",
        "icon": "❌",
        "duration": "long"
    },
    "draft_autosaved": {
        "message": "💾 Draft auto-saved",
        "icon": "💾",
        "duration": "short"
    },
    "no_pending_changes": {
        "message": "✨ No changes to commit",
        "icon": "ℹ️",
        "duration": "short"
    },
    
    # Month operations
    "month_switched": {
        "message": "📅 Month switched",
        "icon": "📅",
        "duration": "short"
    },
    "month_created": {
        "message": "✅ New month created",
        "icon": "✅",
        "duration": "short"
    },
    "month_creation_failed": {
        "message": "❌ Could not create month",
        "icon": "❌",
        "duration": "long"
    },
    "draft_saved": {
        "message": "💾 Draft saved before switching",
        "icon": "💾",
        "duration": "short"
    },
    
    # CSV operations
    "csv_upload_success": {
        "message": "📤 CSV uploaded successfully",
        "icon": "📤",
        "duration": "short"
    },
    "csv_upload_failed": {
        "message": "❌ CSV upload failed",
        "icon": "❌",
        "duration": "long"
    },
    "csv_entries_added": {
        "message": "✅ Entries added from CSV to pending",
        "icon": "✅",
        "duration": "short"
    },
    "csv_export_ready": {
        "message": "✅ CSV export ready for download",
        "icon": "✅",
        "duration": "short"
    },
    "csv_export_failed": {
        "message": "❌ CSV export failed",
        "icon": "❌",
        "duration": "long"
    },
    "csv_no_data": {
        "message": "⚠️ No data to export",
        "icon": "⚠️",
        "duration": "short"
    },
}


def show_toast(notification_type: str, custom_message: str = None, icon: str = None, duration: str = "short") -> None:
    """
    Display a toast notification.
    
    Args:
        notification_type: Key from NOTIFICATIONS dict
        custom_message: Override default message
        icon: Override default icon
        duration: "short", "long", "infinite", or seconds as int
    """
    if notification_type in NOTIFICATIONS:
        notification = NOTIFICATIONS[notification_type]
        message = custom_message or notification["message"]
        icon_val = icon or notification["icon"]
        duration_val = duration or notification["duration"]
    else:
        # Unknown notification type - show generic
        message = custom_message or notification_type
        icon_val = icon or "ℹ️"
        duration_val = duration or "short"
    
    st.toast(message, icon=icon_val, duration=duration_val)


def show_success(message: str, duration: str = "short") -> None:
    """Show success toast."""
    st.toast(message, icon="✅", duration=duration)


def show_error(message: str, duration: str = "long") -> None:
    """Show error toast."""
    st.toast(message, icon="❌", duration=duration)


def show_warning(message: str, duration: str = "long") -> None:
    """Show warning toast."""
    st.toast(message, icon="⚠️", duration=duration)


def show_info(message: str, duration: str = "short") -> None:
    """Show info toast."""
    st.toast(message, icon="ℹ️", duration=duration)


# Context managers for notification patterns
class notification_context:
    """Context manager for showing notifications during operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.success = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            show_error(f"❌ {self.operation_name} failed: {exc_val}")
            return False
        
        if self.success:
            show_success(f"✅ {self.operation_name} completed")
        
        return False


# Batch notification sender
class notification_queue:
    """Queue notifications to be shown together."""
    
    def __init__(self):
        self.notifications = []
    
    def add(self, notification_type: str, custom_message: str = None) -> None:
        """Add notification to queue."""
        self.notifications.append((notification_type, custom_message))
    
    def flush(self) -> None:
        """Send all queued notifications."""
        for notification_type, custom_message in self.notifications:
            show_toast(notification_type, custom_message)
        self.notifications = []
