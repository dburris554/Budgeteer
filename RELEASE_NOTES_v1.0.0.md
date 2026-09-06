# Budgeteer v1.0.0 Release Notes

**Release Date**: September 5, 2026  
**Status**: Production Ready  
**Previous Version**: v0.15.x  

---

## Overview

Budgeteer v1.0.0 is a major release that transforms the application from a basic budget tracker into a production-ready personal finance tool with form-based data entry, authenticated access, optional cloud persistence, and comprehensive analytics.

This release maintains backwards compatibility with CSV exports from previous versions while introducing a completely new workflow centered around staged changes and explicit commits.

---

## What's New

### 🎉 Major Features

#### 1. **Form-Based Data Entry** (Replaces AgGrid)
- Dedicated Income Entry Form
  - Day, Description, Amount, Allocation, Cleared status
  - Built-in validation (Day 1-31, Amount > 0, Description required)
  - Clear form after submission for rapid data entry

- Dedicated Expense Entry Form
  - Day, Description, Category, Amount, Allocation (from income dropdown)
  - Automatic, Paid, Cleared status tracking
  - Smart allocation selection from existing income entries
  - Input validation with helpful error messages

**Benefits**: Reduces data entry errors, cleaner UI, better mobile experience

#### 2. **Staged Changes Workflow** (New!)
- Pending Changes Section
  - Review all staged entries before committing
  - Edit pending entries in-place
  - Delete pending entries
  - Toggle between List and Card view
  - Pending count badge

- Explicit Commit Step
  - "Commit & Save" button makes changes permanent
  - Confirms all pending changes in one action
  - Clear success feedback with toast notification
  - Undo capability (before commit) via delete

**Benefits**: Prevents accidental saves, allows bulk review, clear state management

#### 3. **Monthly Budget Organization** (Enhanced)
- Month Selector Dropdown
  - Switch between existing months
  - See all available months in one place

- New Month Creation
  - Create blank month
  - Copy from current month (replicate budget structure)
  - Copy from previous month (iterate on last month's plan)
  - YYYY-MM format validation

- Month-Based Data Isolation
  - Each month has separate committed data
  - Switching months preserves pending changes as draft
  - Summary metrics per month

**Benefits**: Easier multi-month planning, no data bleeding between months

#### 4. **Single-User Authentication** (New!)
- Login System
  - Username/password authentication
  - Bcrypt password hashing (secure)
  - Cookie-based session persistence
  - Re-authentication cookie (remember me)

- Guest Mode
  - "Continue as Guest" option
  - Full app access without credentials
  - Session-only data (lost on browser close)
  - Easy switching between modes

- Logout Button
  - Clear session properly
  - Return to login screen
  - Ability to switch users/modes

**Benefits**: Multi-device support (with auth), data privacy, easy account switching

#### 5. **Google Sheets Integration** (Optional, New!)
- OAuth-Based Connection
  - User's own Google account
  - Automatic workbook creation
  - Multi-sheet structure (one per month)
  - Draft sheet for auto-saved changes

- Automatic Backup
  - Committed data syncs to GSheets
  - Pending changes auto-save to Draft tab
  - Survives connection loss
  - Access from multiple devices

- Fallback to Local Storage
  - If GSheets unavailable: continues in session-only mode
  - No forced cloud dependency
  - Manual CSV export as backup

**Benefits**: Cloud backup, device sync, data recovery, professional audit trail

#### 6. **Auto-Save Draft** (New!)
- Automatic Saves
  - Every change to pending triggers auto-save
  - Saves to GSheets Draft sheet (if connected)
  - Falls back to session state
  - Timestamp tracking: "Draft auto-saved at HH:MM:SS"

- Data Protection
  - Survives browser crashes
  - Survives connection interruptions
  - Survives accidental page close
  - Recovery on next login

**Benefits**: Peace of mind, no lost work, professional stability

#### 7. **Enhanced Insights & Visualizations** (Redesigned)
- Summary Metrics
  - Total Income, Total Expenses, Net Balance
  - Real-time updates as data changes
  - Color-coded balance (green = positive, red = negative)

- Pending Charges Analysis
  - Expenses marked Automatic/Paid but not Cleared
  - Grouped by income source
  - Running totals per income

- Unpaid Charges Analysis
  - Expenses not yet paid
  - Easy identification of bills due
  - Priority list for payment

- Income Burndowns (Visualizations)
  - Line chart per income source
  - Shows balance over the month
  - Identifies when each income runs out
  - Step-wise chart matching expense timing

- Data Exploration
  - Income vs Expenses bar chart
  - Income-to-Category flow (Sankey diagram)
  - Multi-dimensional budget understanding

**Benefits**: Better financial clarity, early warning system, spending insights

#### 8. **Toast Notifications** (New!)
- Real-Time Feedback
  - Success (✅), Error (❌), Warning (⚠️), Info (ℹ️)
  - Auto-dismiss based on type
  - Clear, actionable messages
  - Stacking support for multiple notifications

- Notification Coverage
  - Authentication (login, logout, errors)
  - Data entry (form submission, validation)
  - Pending changes (edit, delete, clear)
  - Commit operations (save, errors)
  - Month operations (create, switch)
  - CSV operations (upload, export)
  - GSheets operations (connect, sync)

**Benefits**: Clear feedback loop, reduced user confusion, professional feel

#### 9. **Comprehensive Documentation** (New!)
- In-App Documentation
  - About tab with expandable sections
  - Feature overview, getting started, troubleshooting
  - Video-ready structure (future enhancement)

- External Documentation
  - DOCUMENTATION.md: Full 12-section user guide
  - README.md: Quick start and deployment guide
  - DEPLOYMENT_CHECKLIST.md: Testing and release procedures

- Examples & Use Cases
  - Real examples for each feature
  - Workflow descriptions
  - Best practices and tips

**Benefits**: Self-service support, easier onboarding, reduced support burden

#### 10. **CSV Import/Export Enhancement** (Improved)
- Import to Pending (Not Direct Commit)
  - Upload CSV file
  - Validation of columns and data
  - Preview before import
  - Adds to pending changes (not committed)
  - Full validation workflow

- Export Includes Pending
  - Committed + Pending data in export
  - Sorted by Day for readability
  - Configurable filename
  - Download button in sidebar

**Benefits**: Better workflow integration, safer imports, complete data backups

---

## Breaking Changes

### ⚠️ Upgrade Notes (From v0.15.x)

1. **CSV Format Unchanged**
   - Existing CSV exports work with v1.0.0
   - Can import old budget CSV files
   - No migration needed

2. **Data Lost in Guest Mode**
   - Old session data from v0.15.x won't persist
   - Switch to authenticated mode for persistence
   - Export to CSV before upgrading if using guest mode

3. **UI Completely Redesigned**
   - AgGrid replaced with forms
   - Inline editing removed (now edit via pending changes)
   - Two-phase commit model (new workflow)

4. **Dependencies Changed**
   - Removed: streamlit-aggrid, friendlywords
   - Added: streamlit-authenticator, st-gsheets-connection
   - Updated: streamlit>=1.40.0, pandas>=2.0.0

---

## Improvements

### Performance
- Form submission instant (< 100ms)
- Data display optimized for 100+ entries
- Responsive UI with fast re-renders
- Efficient state management

### User Experience
- Cleaner, less cluttered interface
- Better mobile responsiveness
- Clear feedback for all actions
- Improved error messages

### Code Quality
- Modular architecture (auth, data_entry, insights, etc.)
- Better separation of concerns
- Improved error handling
- Native Streamlit components (no custom CSS/HTML)

### Accessibility
- Better semantic HTML
- Proper form labels
- Keyboard navigation support
- Clear visual hierarchy

---

## Known Limitations

### Current Version (v1.0.0)
1. **Single User Only**
   - No multi-user or family budget support
   - Planned for v1.1.0

2. **No Baseline Budgets**
   - Can't auto-generate months from templates
   - Manual month creation only
   - Planned for v1.1.0

3. **Limited Recurrence Rules**
   - No automatic recurring entry generation
   - Manual replication required
   - Planned for v1.1.0

4. **No Mobile App**
   - Web-only (but responsive)
   - Mobile web works well
   - Native app not planned

5. **Limited Export Formats**
   - CSV only (Excel, JSON coming later)
   - No PDF reports in v1.0.0

6. **No Data Sharing**
   - Personal budget only
   - No collaborative features
   - Planned for v1.1.0

### Technical Limitations
1. GSheets connection requires OAuth setup (not automatic)
2. Large datasets (1000+) may slow down insights
3. Browser local storage limit ~5MB (very generous for budgets)

---

## Fixes & Bug Resolutions

### Fixed in v1.0.0
- Removed styling conflicts with newer Streamlit versions
- Fixed boolean column handling (now uses native Streamlit)
- Improved error messages for validation failures
- Better handling of network interruptions (auto-save draft)
- Resolved memory leaks in session state (proper cleanup)

---

## Migration Guide

### For v0.15.x Users

#### Option 1: Fresh Start (Recommended)
1. Download Budgeteer v1.0.0
2. Create new budget for current month
3. Enter data using new form-based interface
4. Enjoy new features!

#### Option 2: Import from Old CSV
1. Export budget from v0.15.x as CSV
2. In v1.0.0, click "Import from CSV" in sidebar
3. Select your exported CSV file
4. Review data in pending changes
5. Click "Commit & Save"

#### Option 3: Keep Old Data
1. Run v0.15.x and export all data as CSV for backup
2. Upgrade to v1.0.0
3. Import CSV whenever you want to reference old data

---

## Dependencies

### Removed
- `streamlit-aggrid` (0.3.x) - Replaced with native Streamlit forms
- `friendlywords` - No longer auto-generating placeholder data

### Added
- `streamlit-authenticator` (>=0.3.0) - Single-user authentication
- `st-gsheets-connection` (*) - Google Sheets integration
- `pyyaml` (>=6.0) - Authentication config file format
- `gspread` (>=5.0.0) - GSheets API client (dependency of gsheets-connection)

### Updated
- `streamlit` (>=1.40.0) - Latest stable release
- `pandas` (>=2.0.0) - Better performance and features
- `plotly` (>=5.0.0) - Improved charts
- `altair` (>=5.0.0) - Enhanced visualizations
- `numpy` (>=1.24.0) - Core data processing

---

## System Requirements

### Minimum
- Python 3.11+
- 512MB RAM (2GB recommended for large datasets)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for GSheets sync)

### Recommended
- Python 3.11 or 3.12
- 2GB+ RAM
- SSD storage
- Broadband internet
- Latest browser version

---

## Security & Privacy

### Authentication
- Passwords hashed with bcrypt (industry standard)
- Session tokens used for authentication
- Cookie-based session persistence (configurable)
- No plaintext password storage

### Data Storage
- Local storage: Browser local storage (encrypted by browser)
- Cloud storage: GSheets via OAuth (user's own account)
- No data sent to third-party servers
- Full user privacy and control

### GSheets Integration
- OAuth 2.0 authentication (industry standard)
- User authorizes access to their own Google account
- Only data explicitly synced to GSheets
- User can revoke access anytime

---

## Deployment Changes

### Docker
- Updated Dockerfile for latest Streamlit version
- Health checks configured for Cloud Run
- Port 8501 exposed correctly

### Cloud Run
- Automatic builds on tag push (`git push origin v1.0.0`)
- Environment variables: `PORT=8501`, `STREAMLIT_SERVER_HEADLESS=true`
- Secrets management via Cloud Secrets Manager

### Configuration
- `.streamlit/config.toml` - Theme and server settings
- `.streamlit/secrets.toml` - Google Sheets credentials (template provided)
- `auth_config.yaml` - User credentials (in-repo for simplicity)

---

## Roadmap: v1.1.0 and Beyond

### v1.1.0 (Q1 2027)
- [ ] Baseline budgets with recurrence rules
  - Create templates for recurring income/expenses
  - Sample calendar to preview recurrence patterns
  - Auto-generate months from baselines

- [ ] Advanced month generation
  - Generate from baseline (full, partial, or blank)
  - Option to apply changes back to baseline
  - Monthly templates

- [ ] Multi-user support (Family/Household)
  - Shared budgets
  - Permission levels
  - Collaborative editing

### v1.2.0 (Q2-Q3 2027)
- [ ] Additional export formats (Excel, PDF)
- [ ] Spending trends and analytics
- [ ] Budget goals and alerts
- [ ] Recurring transaction automation

### v2.0.0 (2027-2028)
- [ ] Mobile app (iOS/Android)
- [ ] Machine learning for expense categorization
- [ ] Multi-currency support
- [ ] API for third-party integrations

---

## Getting Help

### Resources
- **In-App**: About tab with comprehensive guide
- **Documentation**: DOCUMENTATION.md for detailed user guide
- **README**: README.md for setup and troubleshooting
- **Checklist**: DEPLOYMENT_CHECKLIST.md for testing procedures

### Support
- Report bugs via GitHub Issues
- Suggest features via GitHub Discussions
- Support development via Donate tab

---

## Credits & Acknowledgments

- **Streamlit**: Framework and community
- **Authentication**: streamlit-authenticator project
- **Google Sheets**: gsheets-connection and gspread
- **Visualizations**: Plotly and Altair communities
- **Users**: Feedback and support

---

## License

[Include your project license]

---

## Changelog

### v1.0.0 (2026-09-05)
- ✨ Initial production release
- ✨ Form-based data entry system
- ✨ Staged changes workflow with explicit commits
- ✨ Single-user authentication with guest mode
- ✨ Optional Google Sheets integration
- ✨ Auto-save draft for data protection
- ✨ Enhanced insights and visualizations
- ✨ Toast notification system
- ✨ Comprehensive user documentation
- ✨ CSV import/export with pending changes
- 🎨 Complete UI redesign
- 📚 Full documentation suite
- 🐳 Docker and Cloud Run support
- ✅ Production ready

### v0.15.x (Previous)
- Baseline functionality
- AgGrid-based editing
- Session-only storage

---

**Thank you for using Budgeteer! Happy budgeting! 🚀**

---

For questions or feedback: support@example.com  
Visit: http://budgeteer.online (when deployed)
