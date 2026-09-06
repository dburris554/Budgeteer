# Budgeteer v1.0.0 - Deployment Checklist

## Pre-Release Testing

### Authentication Testing
- [ ] **Login Flow**
  - [ ] Test with correct credentials - should log in successfully
  - [ ] Test with incorrect password - should show error
  - [ ] Test with non-existent username - should show error
  - [ ] Toast notification shows on successful login
  - [ ] Toast notification shows on logout

- [ ] **Guest Mode**
  - [ ] "Continue as Guest" button works
  - [ ] Guest can access full app features
  - [ ] Data persists during session
  - [ ] Data is lost on browser close (expected behavior)

- [ ] **Session Management**
  - [ ] Logout button appears when logged in
  - [ ] Logout clears authentication
  - [ ] Can re-login after logout
  - [ ] Session persists on page refresh (logged in)
  - [ ] Guest session persists on page refresh

### Data Entry Testing
- [ ] **Income Form**
  - [ ] Form appears with all required fields
  - [ ] Day validation: rejects 0, 32, negative numbers
  - [ ] Amount validation: rejects 0, negative numbers
  - [ ] Description validation: rejects empty
  - [ ] Form clears after successful submission
  - [ ] Entry appears in Pending Changes immediately
  - [ ] Toast notification shows after submission

- [ ] **Expense Form**
  - [ ] Form appears with all required fields
  - [ ] Category dropdown populates from income descriptions
  - [ ] Day/Amount/Description validation works same as income
  - [ ] Category validation: rejects empty
  - [ ] Allocation validation: requires selection from dropdown
  - [ ] Checkboxes for Automatic, Paid, Cleared work
  - [ ] Form clears after successful submission
  - [ ] Entry appears in Pending Changes immediately
  - [ ] Toast notification shows after submission

### Pending Changes Testing
- [ ] **Display**
  - [ ] Pending changes appear immediately after form submission
  - [ ] Pending count badge shows correct number
  - [ ] List view shows all entries with type badges
  - [ ] Card view shows all entries in grid layout
  - [ ] View toggle switches between list and cards

- [ ] **Editing**
  - [ ] Edit button populates form with pending entry data
  - [ ] Edit form allows modification of all fields
  - [ ] Save update reflects changes in pending list
  - [ ] Cancel edit closes form without changes
  - [ ] Toast shows on successful edit

- [ ] **Deleting**
  - [ ] Delete button removes entry from pending list
  - [ ] Toast notification shows on deletion
  - [ ] "Clear All" button removes all pending entries
  - [ ] Clear All warns user with description

### Commit/Save Testing
- [ ] **Commit Operation**
  - [ ] "Commit & Save" button is disabled when no pending changes
  - [ ] "Commit & Save" button is enabled when pending changes exist
  - [ ] Click commits all pending changes
  - [ ] Pending list clears after commit
  - [ ] Success toast shows
  - [ ] Committed entries appear in "Committed Entries" section

- [ ] **Draft Auto-Save**
  - [ ] Draft auto-saves on every pending change
  - [ ] Timestamp updates after each auto-save
  - [ ] Switching months auto-saves draft
  - [ ] Draft persists if connection drops

### Committed Data Display Testing
- [ ] **Table Rendering**
  - [ ] Empty state shows helpful message
  - [ ] Data displays in table format
  - [ ] Entries sorted by Day (ascending)
  - [ ] Amounts formatted as currency ($X,XXX.XX)
  - [ ] Day shows as integer
  - [ ] Boolean columns show as checkboxes (read-only)
  - [ ] Entry count by category shows correctly

### Month Management Testing
- [ ] **Month Selector**
  - [ ] Dropdown shows all available months
  - [ ] Can select different months
  - [ ] Switching months loads correct data
  - [ ] Summary metrics update for selected month

- [ ] **Month Creation**
  - [ ] "New Month" button opens creation dialog
  - [ ] Date input validates YYYY-MM format
  - [ ] "Blank" option creates empty month
  - [ ] "Current Month" copies all entries
  - [ ] "Previous Month" option works (if available)
  - [ ] Cancel button closes dialog without creating
  - [ ] Toast shows on successful creation

### Insights Testing
- [ ] **Summary Metrics**
  - [ ] Total Income calculates correctly
  - [ ] Total Expenses calculates correctly
  - [ ] Net Balance = Income - Expenses
  - [ ] Metrics update when data changes

- [ ] **Pending Charges**
  - [ ] Expander collapses/expands
  - [ ] Shows expenses marked as Automatic or Paid but not Cleared
  - [ ] Groups by income allocation correctly
  - [ ] Sum calculations correct

- [ ] **Unpaid Charges**
  - [ ] Shows expenses not paid and not cleared
  - [ ] Sum calculations correct
  - [ ] Empty state handled gracefully

- [ ] **Income Burndowns**
  - [ ] Charts render for each income
  - [ ] Line starts at income day
  - [ ] Line drops as expenses are deducted
  - [ ] Final balance correct

- [ ] **Data Exploration**
  - [ ] Bar chart shows income vs expenses
  - [ ] Sankey diagram shows income flow to categories
  - [ ] Empty state when no data

### CSV Testing
- [ ] **Import**
  - [ ] File picker opens
  - [ ] CSV with correct columns parsed successfully
  - [ ] CSV with missing columns shows error
  - [ ] Preview shows data accurately
  - [ ] Data validates (Day 1-31, Amount numeric)
  - [ ] "Add to Pending" adds all rows
  - [ ] Entries appear in pending list
  - [ ] Toast shows with count

- [ ] **Export**
  - [ ] Download button appears
  - [ ] CSV exports with correct columns
  - [ ] Filename input works
  - [ ] Exported file contains all committed + pending data
  - [ ] Data sorted by Day
  - [ ] Toast shows on download

### GSheets Integration Testing (if enabled)
- [ ] **Connection**
  - [ ] OAuth flow prompts for authorization
  - [ ] Connection establishes successfully
  - [ ] Toast shows connection status

- [ ] **Data Sync**
  - [ ] Committed data saves to GSheets
  - [ ] Draft tab receives auto-save data
  - [ ] Multiple months create separate tabs
  - [ ] Data persists after logout/login

### Toast Notifications Testing
- [ ] **Success Toasts** (✅)
  - [ ] Show green checkmark
  - [ ] Auto-dismiss after short duration
  - [ ] Provide clear confirmation message

- [ ] **Error Toasts** (❌)
  - [ ] Show red X
  - [ ] Longer display duration
  - [ ] Clear error description

- [ ] **Info Toasts** (ℹ️)
  - [ ] Show info icon
  - [ ] Appear for informational messages

---

## Performance Testing

### Load Time
- [ ] App loads in < 3 seconds on first visit
- [ ] Subsequent loads < 1 second (caching)
- [ ] Form submissions responsive (< 1 second)
- [ ] Data updates smooth and responsive

### Large Data Sets
- [ ] 100+ entries load without lag
- [ ] 200+ entries display (reasonable performance)
- [ ] Sorting/filtering still responsive

### Responsive Design
- [ ] [ ] Mobile (320px): Layout adapts, readable
- [ ] Tablet (768px): Layout adapts properly
- [ ] Desktop (1920px): Uses full width efficiently

---

## Security Testing

### Password Security
- [ ] [ ] Passwords hashed (not stored plain text)
- [ ] [ ] Password validation requirements enforced
- [ ] [ ] Session tokens used for authentication
- [ ] [ ] Logout clears session properly

### Data Validation
- [ ] [ ] All form inputs validated
- [ ] [ ] Malformed CSV rejected gracefully
- [ ] [ ] SQL injection not possible (using gspread library)
- [ ] [ ] XSS protection via Streamlit

### GSheets Security (if enabled)
- [ ] [ ] OAuth uses official Google credentials
- [ ] [ ] Secrets stored securely (not in code)
- [ ] [ ] Only authenticated user can access their data

---

## Browser Compatibility

- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Android)

---

## Documentation Review

- [ ] [ ] README.md complete and accurate
- [ ] [ ] DOCUMENTATION.md covers all features
- [ ] [ ] About tab helpful and clear
- [ ] [ ] All sections have examples
- [ ] [ ] Troubleshooting covers common issues
- [ ] [ ] Setup instructions tested and work

---

## Deployment Preparation

### Code Quality
- [ ] [ ] All deprecation warnings addressed
- [ ] [ ] No hardcoded secrets or credentials
- [ ] [ ] No debug prints or logging clutter
- [ ] [ ] Code follows PEP 8 style
- [ ] [ ] Imports organized and cleaned up

### Dependencies
- [ ] [ ] Pipfile updated with correct versions
- [ ] [ ] requirements.txt generated and tested
- [ ] [ ] No unused dependencies
- [ ] [ ] No conflicting versions

### Configuration
- [ ] [ ] .streamlit/config.toml theme configured
- [ ] [ ] .streamlit/secrets.toml.template provided
- [ ] [ ] auth_config.yaml template provided
- [ ] [ ] All config files documented

### Git & Version Control
- [ ] [ ] All changes committed
- [ ] [ ] No uncommitted work
- [ ] [ ] .gitignore excludes secrets/cache
- [ ] [ ] Clean git history (no temp commits)

### Docker & Cloud Run
- [ ] [ ] Dockerfile builds successfully
- [ ] [ ] App runs in container as expected
- [ ] [ ] Port 8501 exposed correctly
- [ ] [ ] Health checks pass
- [ ] [ ] Environment variables work in container

### Release Notes
- [ ] [ ] v1.0.0 release notes written
- [ ] [ ] Major features documented
- [ ] [ ] Known limitations listed
- [ ] [ ] Migration notes from v0.15.x

---

## Go/No-Go Decision

### Must Have (All Required)
- [ ] Authentication works (login/logout/guest)
- [ ] Data entry forms work with validation
- [ ] Commit/save functionality works
- [ ] CSV import/export works
- [ ] Insights tab displays correctly
- [ ] No critical errors or crashes
- [ ] Documentation complete

### Nice to Have (Not Required for v1.0.0)
- [ ] GSheets integration working
- [ ] All browsers tested
- [ ] Performance optimized
- [ ] Accessibility reviewed

### Go/No-Go: **[ ] GO** / **[ ] NO-GO**

If NO-GO, list blockers:
```
1. 
2. 
3. 
```

---

## Post-Release

### Deployment Steps
1. [ ] Create release tag: `git tag v1.0.0`
2. [ ] Push tag: `git push origin v1.0.0`
3. [ ] Verify Cloud Run deployment triggered
4. [ ] Test deployed app at production URL
5. [ ] Monitor error logs for 24 hours
6. [ ] Announce release

### Post-Release Monitoring
- [ ] Monitor error rates in Cloud Run logs
- [ ] Monitor performance metrics
- [ ] Respond to user feedback quickly
- [ ] Plan hotfixes if needed

---

## Sign-Off

- **Tester**: _________________ **Date**: _______
- **Developer**: _________________ **Date**: _______
- **Release Manager**: _________________ **Date**: _______

---

**Version**: 1.0.0  
**Created**: 2026-09-05  
**Last Updated**: [TODAY]
