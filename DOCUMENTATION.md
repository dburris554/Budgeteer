# Budgeteer v1.0.0 User Guide

## Table of Contents
1. [Welcome](#welcome)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [Managing Monthly Budgets](#managing-monthly-budgets)
5. [Adding Income & Expenses](#adding-income--expenses)
6. [Pending Changes Workflow](#pending-changes-workflow)
7. [Committing Changes](#committing-changes)
8. [Insights & Visualizations](#insights--visualizations)
9. [CSV Import/Export](#csv-importexport)
10. [Google Sheets Integration](#google-sheets-integration-optional)
11. [Tips & Tricks](#tips--tricks)
12. [Troubleshooting](#troubleshooting)

---

## Welcome

**Budgeteer** is a personal budget planning application that helps you organize your income, track expenses, and understand your financial flow throughout the month.

### Key Features

- **📝 Form-Based Data Entry** - Structured forms for adding income and expenses without table clutter
- **📅 Monthly Budget Organization** - Create separate budgets for each month
- **⏳ Staged Changes Workflow** - Review changes before committing to prevent errors
- **💾 Optional Google Sheets Integration** - Cloud backup and persistent storage
- **🔐 Single-User Authentication** - Secure password protection
- **📊 Interactive Visualizations** - Charts and graphs to understand your budget
- **💾 Draft Auto-Save** - Automatic backup of uncommitted changes
- **📥 CSV Import/Export** - Import existing budgets or export for external analysis
- **👤 Guest Mode** - Try the app without authentication (session-only)

---

## Getting Started

### First Time Users

1. **Choose Your Access Mode**
   - **Login**: Enter your credentials for persistent storage with Google Sheets
   - **Guest Access**: Continue without an account (data stored in browser session only)

2. **Create or Select a Month**
   - Use the "📅 Monthly Budget" selector in the sidebar
   - Click "➕ New Month" to create a new monthly budget
   - Choose to start blank or copy from current/previous month

3. **Add Your First Entry**
   - Click "➕ Add Income" or "➕ Add Expense"
   - Fill out the form fields
   - Submit - your entry will appear in the Pending Changes section

4. **Review and Commit**
   - Check the "Pending Changes" section to verify your entries
   - Click "✅ Commit & Save" to save everything to your budget
   - Your entries will appear in the "Committed Entries" section

5. **Explore Insights**
   - Switch to the "Insights" tab to view your budget analysis
   - See visualizations of income vs expenses, pending charges, burndowns, and more

---

## Authentication

### Login

1. Click the "Login" tab on the login page
2. Enter your username and password
3. Click "Login to Budgeteer"
4. On successful login, you'll access the main app with Google Sheets integration enabled

**Note:** Your credentials are managed securely using Streamlit-Authenticator with bcrypt password hashing.

### Guest Access

1. Click the "Guest Access" tab on the login page
2. Click "Continue as Guest"
3. Your budget data will be stored in your browser session only
4. **Important:** Data will be lost when you close the browser or navigate away

### Logout

- Click the "🚪 Logout" button in the sidebar to log out
- You can then log in again or continue as a guest

### Switching Between Modes

- Log out to return to the login screen
- Choose a different access mode (Login or Guest)
- Your previous data will be preserved in both modes

---

## Managing Monthly Budgets

### Creating a New Month

1. Click the "➕ New Month" button in the sidebar
2. Enter the month in `YYYY-MM` format (e.g., `2024-03` for March 2024)
3. Choose your starting data:
   - **Blank**: Start with an empty budget
   - **Current Month**: Copy all entries from the currently selected month
   - **Previous Month**: Copy entries from the previous month (if available)
4. Click "Create" to create the month

### Switching Between Months

1. Use the "Select Month" dropdown in the sidebar
2. Click the month you want to view
3. Your pending changes from the previous month will be auto-saved to draft
4. The new month's data will load automatically

### Viewing Month Summary

The summary metrics at the top of the Data tab show:
- **💰 Total Income**: Sum of all income entries
- **💸 Total Expenses**: Sum of all expense entries
- **📊 Net Balance**: Total Income minus Total Expenses

---

## Adding Income & Expenses

### Income Entry Form

The income form captures recurring or one-time income sources.

**Fields:**
- **Day of Month** (1-31): What day will this income arrive?
- **Description**: Name or type of income (e.g., "Paycheck", "Bonus")
- **Amount ($)**: Income amount in dollars
- **Allocation (Bank/Source)**: Which account receives this income (e.g., "Chase", "PayPal")
- **Marked as Cleared**: Is this income cleared (received)?

**Example:** A paycheck arriving on the 1st for $2,000 deposited to "Main Bank"

### Expense Entry Form

The expense form tracks costs that deplete income.

**Fields:**
- **Day of Month** (1-31): When will this expense occur?
- **Description**: Name or type of expense (e.g., "Rent", "Groceries")
- **Category**: Type of expense (e.g., "Housing", "Food", "Medical")
- **Amount ($)**: Expense amount in dollars
- **Paid from**: Which income source covers this expense (dropdown from existing incomes)
- **Automatic Payment**: Is this automatically deducted?
- **Paid**: Has this expense been paid?
- **Cleared**: Has this expense cleared the account?

**Example:** Rent of $1,200 on the 1st, paid automatically from "Paycheck"

### Form Validation

Both forms validate your input:
- **Day**: Must be between 1 and 31
- **Amount**: Must be greater than 0
- **Description**: Cannot be empty
- **Category** (expenses only): Cannot be empty
- **Allocation/Paid from**: Required field

If validation fails, you'll see an error message. Fix the error and resubmit.

---

## Pending Changes Workflow

### Understanding Pending Changes

When you add, edit, or delete entries, they don't immediately become part of your committed budget. Instead, they're staged in a "pending" state, allowing you to review before committing.

**Benefits:**
- Catch and fix errors before saving
- Review all changes at once
- Undo changes by deleting them from pending
- See a clear before/after of your budget

### Viewing Pending Changes

The "⏳ Pending Changes" section shows all staged entries with:

- **Type badge**: ➕ (Add), ✏️ (Edit), 🗑️ (Delete)
- **Entry details**: Description, amount, day, category
- **Edit button** (✏️): Modify the pending entry
- **Delete button** (🗑️): Remove from pending list

### Switching Views

Toggle between two viewing modes:

1. **List View** (default): Compact list of pending changes
2. **Cards View**: Grid layout with larger, easier-to-read cards

Click the toggle to switch between views based on your preference.

### Editing Pending Changes

1. Click the ✏️ (Edit) button on a pending entry
2. An edit form will appear below the pending list
3. Modify the fields as needed
4. Click "✅ Save" to update the entry or "❌ Cancel" to discard changes

### Deleting Pending Changes

Click the 🗑️ (Delete) button on a pending entry to remove it from your pending list.

**Note:** This only removes it from pending—it won't affect committed entries.

### Clear All Pending

Click "🗑️ Clear All" to remove all pending changes at once. Use carefully!

---

## Committing Changes

### What Does "Commit" Mean?

Committing moves all pending changes into your committed budget. Once committed:
- Entries are permanently saved (to local storage and Google Sheets if authenticated)
- Pending list is cleared
- Committed entries appear in the "📋 Committed Entries" section

### How to Commit

1. Review your pending changes in the "⏳ Pending Changes" section
2. Make any edits or deletions as needed
3. Click "✅ Commit & Save" button
4. You'll see a success toast: "✅ Changes committed successfully!"
5. Your committed entries will now appear below

### Draft Auto-Save

Budgeteer automatically saves your pending changes to a draft:
- **When**: Every time you make changes (add, edit, delete)
- **Where**: Locally in your browser and to Google Sheets (if authenticated)
- **Why**: Protection against connection loss or browser crashes

You'll see "📝 Draft auto-saved at HH:MM:SS" to confirm the save.

### Commit Preview

Before committing, you can see a preview of what will be committed:
- Click "Preview changes" in the Save & Commit section
- See a numbered list of all pending changes
- Confirm this is what you want to commit

---

## Insights & Visualizations

The **Insights** tab provides comprehensive analysis of your committed budget.

### Summary Metrics

At the top, see three key metrics:
- **💰 Total Income**: All income entries combined
- **💸 Total Expenses**: All expense entries combined
- **📊 Net Balance**: Income minus Expenses (positive = surplus, negative = deficit)

### Pending Charges

Analyzes expenses that are marked as automatic or paid but haven't cleared yet.

**Shows:**
- Grouped by income allocation (bank/account)
- For each income source: pending expenses and their total
- Cleared status indicator

**Use Case:** Track expenses that have been paid but haven't fully cleared your account.

### Unpaid Charges

Shows expenses that are marked as unpaid and not cleared.

**Shows:**
- Expenses flagged as unpaid (Automatic=False, Paid=False)
- Total unpaid amount per income source
- List of unpaid entries

**Use Case:** Identify bills you still need to pay this month.

### Income Burndowns

Line charts showing how your balance changes throughout the month.

**Shows:**
- One chart per income source
- Balance starts at income amount on the income day
- Balance decreases as expenses are deducted
- Final balance at the end of the month

**Use Case:** Visualize when you'll run out of money from each income source.

### Data Exploration

**Income vs Expenses Bar Chart:**
- Side-by-side comparison of total income and total expenses
- Quickly see if you're spending more than you earn

**Income-Expense Flow (Sankey Diagram):**
- Flow chart showing how income flows into expense categories
- Width of flow represents money amount
- Reveals which categories consume your income

---

## CSV Import/Export

### CSV Format

Budgeteer uses CSV (Comma-Separated Values) format with the following columns:

```
Day,Description,Category,Amount,Allocation,Automatic,Paid,Cleared
1,Paycheck,Income,2000.00,Main Bank,False,False,True
5,Rent,Housing,1200.00,Paycheck,True,False,False
```

**Column Descriptions:**
- `Day`: 1-31 (day of month)
- `Description`: Entry name (e.g., "Paycheck", "Groceries")
- `Category`: Entry type (Income, Housing, Food, etc.)
- `Amount`: Dollar amount (positive number)
- `Allocation`: Source account or income (e.g., "Main Bank", "Paycheck")
- `Automatic`: True/False
- `Paid`: True/False
- `Cleared`: True/False

### Importing CSV

1. In the sidebar, go to "📤 Import from CSV"
2. Click "Upload budget CSV"
3. Select a `.csv` file from your computer
4. Budgeteer will:
   - Validate the file format
   - Check for required columns
   - Show a preview of the data
5. Click "➕ Add to Pending" to import
6. Entries will appear in your Pending Changes section
7. Review and commit as normal

**Tips:**
- Make sure your CSV has the exact column names
- Validate amounts are numbers
- Days must be 1-31

### Exporting to CSV

1. In the sidebar, go to "📥 Export to CSV"
2. (Optional) Change the filename
3. Click "📋 Prepare Download"
4. Review the preview
5. Click "⬇️ Download [filename].csv"
6. The file will download to your computer

**What Gets Exported:**
- All committed entries
- All pending (uncommitted) entries combined
- Sorted by day for easy reading

**Use Cases:**
- Backup your budget
- Import into spreadsheet programs
- Share with an accountant
- Analyze in Excel or Google Sheets

---

## Google Sheets Integration (Optional)

### What It Does

When you log in with authentication, Budgeteer can optionally sync your budget to Google Sheets:
- Automatic backup of committed data
- Access your budget from multiple devices
- Share with others (future feature)
- Permanent cloud storage

### How to Set Up

1. **Enable Google Sheets API** (admin setup):
   - Go to Google Cloud Console
   - Create a new project or select existing
   - Enable "Google Drive API" and "Google Sheets API"
   - Create OAuth 2.0 credentials

2. **In Budgeteer**:
   - Log in with your credentials
   - If not already connected, Budgeteer will prompt for Google authorization
   - Authorize access to your Google account
   - Connection established ✅

3. **Your Data**:
   - Budgeteer creates a workbook named "Budgeteer_Budget"
   - One sheet per month (e.g., "2024-01", "2024-02")
   - "Draft" sheet for backup of uncommitted changes

### If Google Sheets Connection Fails

- Budgeteer will continue to work in **session-only mode**
- Your data is saved locally in your browser
- A warning will show: "⚠️ Google Sheets unavailable, using local storage"
- Export to CSV to backup your data

---

## Tips & Tricks

### Organizing Your Budget

1. **Use consistent category names**
   - Pick a set of categories and stick with them
   - Examples: Housing, Food, Transportation, Utilities, Medical, Entertainment
   - Consistent naming improves insights accuracy

2. **Set allocation names carefully**
   - Use recognizable bank/account names
   - Examples: "Main Bank", "Savings", "Paycheck", "Spouse"
   - Keep names consistent across months

3. **Track payment status**
   - Mark `Paid` when you pay the bill
   - Mark `Cleared` when it clears your account
   - Helps you understand cash flow timing

### Workflow Tips

1. **Start with income**
   - Add all your income sources first (paychecks, bonuses, side gigs)
   - This populates the allocation dropdown for expenses

2. **Group by allocation**
   - If you have multiple paychecks, create separate income entries
   - This helps you see which paycheck runs out first

3. **Use pending changes wisely**
   - Add all entries for the week/month, then commit once
   - Use edit/delete liberally before committing
   - Prevents accidental saves

4. **Check insights weekly**
   - Monitor your burndown charts
   - Catch spending patterns early
   - Adjust in pending before committing

### Analyzing Your Budget

1. **Income Burndowns**
   - Flat line = income is lasting the full month ✅
   - Dropping to zero = you'll run out mid-month ⚠️
   - Sharp drops = large expenses on that day

2. **Pending vs Unpaid**
   - Pending = you've paid but it hasn't cleared yet
   - Unpaid = you haven't paid yet
   - Focus on unpaid to see what's still due

3. **Net Balance**
   - Positive = you'll have leftover money
   - Negative = you'll overspend this month
   - Plan to reduce expenses or increase income

---

## Troubleshooting

### "Login Failed" Error

**Cause:** Incorrect username or password

**Solution:**
1. Double-check your credentials
2. Check if Caps Lock is on
3. Remember passwords are case-sensitive

### "No Data to Analyze" in Insights

**Cause:** You haven't committed any entries yet

**Solution:**
1. Add entries using the income/expense forms
2. Click "✅ Commit & Save"
3. Return to Insights to see visualizations

### CSV Import Shows Errors

**Cause:** File format or data issues

**Solution:**
1. Check all required columns are present:
   - Day, Description, Category, Amount, Allocation, Automatic, Paid, Cleared
2. Ensure Day values are 1-31
3. Ensure Amount values are numbers (no $ signs)
4. Save CSV as UTF-8 encoding

### Draft Not Auto-Saving

**Cause:** Google Sheets not connected or network issue

**Solution:**
1. Check internet connection
2. Verify Google Sheets authorization
3. Export to CSV to backup manually
4. Check the About tab for connection status

### Lost My Data

**Cause:** Closed browser without committing (guest mode), or cleared browser cache

**Solution (Guest Mode):**
- Unfortunately, guest mode data is lost
- Use Authentication mode and Google Sheets for persistence

**Solution (Authenticated Mode):**
- Your committed data should be in Google Sheets
- Try logging back in from a different browser
- Contact support with your account details

### Month Selector Shows No Months

**Cause:** This is your first time using Budgeteer

**Solution:**
1. Click "➕ New Month" in the sidebar
2. Enter current month in `YYYY-MM` format
3. Choose "Blank" to start fresh
4. Create the month

---

## Support

- **About Tab**: Version info and quick reference
- **This Documentation**: Full user guide with examples
- **Toast Notifications**: Real-time feedback for your actions
- **Donate Tab**: Support development if you find Budgeteer helpful!

---

## Version Information

**Budgeteer v1.0.0**
- Initial production release
- Form-based data entry
- Monthly budget organization
- Staged changes workflow
- Google Sheets integration (optional)
- Single-user authentication

**Planned for v1.1.0+:**
- Baseline budgets with recurrence rules
- Automatic month generation
- Multi-user support (family/household budgets)
- Advanced reporting and analytics

---

Thank you for using Budgeteer! Happy budgeting! 🚀
