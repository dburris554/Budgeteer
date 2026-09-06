# Budgeteer v1.0.0

Personal budget planning application with form-based data entry, monthly budget organization, and optional Google Sheets integration.

## Features

- 📝 **Form-Based Data Entry** - Structured forms for income and expenses
- 📅 **Monthly Budgets** - Organize budgets by month
- ⏳ **Staged Changes** - Review pending changes before committing
- 💾 **Auto-Save Draft** - Backup uncommitted changes automatically
- ☁️ **Google Sheets Integration** - Optional cloud persistence
- 🔐 **Authentication** - Single-user password protection
- 📊 **Interactive Insights** - Charts and visualizations
- 📥 **CSV Import/Export** - Backup and data portability
- 👤 **Guest Mode** - Try without authentication

## Quick Start

### Prerequisites

- Python 3.11+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Budgeteer
   ```

2. **Set up development environment**
   
   Using the dev container (recommended):
   ```bash
   # Open in VS Code with Dev Container extension
   # or use: devcontainer up
   ```
   
   Or manually with pipenv:
   ```bash
   pip install pipenv
   pipenv install
   pipenv run streamlit run app.py
   ```

3. **Configure authentication** (optional)
   - Edit `auth_config.yaml` with your credentials
   - Change default password in the file
   - Password will be auto-hashed on first run

4. **Configure Google Sheets** (optional)
   - Set up OAuth in Google Cloud Console
   - Create `.streamlit/secrets.toml` from template
   - Add your Google credentials

### Running the App

```bash
# Using pipenv
pipenv run streamlit run app.py

# Or directly with streamlit
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Deployment

### Google Cloud Run

The app is configured for deployment to Google Cloud Run with automatic builds on tag push.

**Setup:**
1. Build and push to Cloud Run
2. Set `PORT=8501` in Cloud Run environment
3. Configure secrets via Cloud Secrets Manager

**Dockerfile is included and will:**
- Install dependencies via pipenv
- Run on port 8501
- Include health checks

### Deployment Commands

```bash
# Tag a release
git tag v1.0.0

# Push to trigger Cloud Run build
git push origin v1.0.0
```

The app will be automatically built and deployed!

## Configuration

### Environment Variables

- `PORT`: Server port (default 8501)
- `STREAMLIT_SERVER_HEADLESS`: true (for Cloud Run)

### Secrets (`.streamlit/secrets.toml`)

For Google Sheets integration (optional):
```toml
[connections.gsheets]
# OAuth configuration here (auto-handled by Streamlit)
```

For authentication, edit `auth_config.yaml` directly (committed to repo for simplicity).

## Documentation

- **In-App**: Click "About" tab for full guide
- **File**: See `DOCUMENTATION.md` for detailed user guide

## Usage Tips

1. **Start with login or guest mode**
   - Login: Persistent storage with Google Sheets
   - Guest: Session-only (data lost on browser close)

2. **Create a monthly budget**
   - Use "New Month" button
   - Copy from previous month or start blank

3. **Add entries using forms**
   - Click "Add Income" or "Add Expense"
   - Submit to stage in pending changes

4. **Review and commit**
   - Check pending changes section
   - Click "Commit & Save" to make permanent

5. **Explore insights**
   - Switch to Insights tab
   - View charts and budget analysis

## Project Structure

```
.
├── app.py                 # Main application
├── auth.py               # Authentication module
├── auth_config.yaml      # User credentials
├── data_entry.py         # Form-based data entry
├── pending_changes.py    # Staged changes workflow
├── commit.py             # Save/commit operations
├── month_manager.py      # Month selection and management
├── gsheets_manager.py    # Google Sheets operations
├── csv_handler.py        # CSV import/export
├── insights.py           # Analysis and visualizations
├── notifications.py      # Toast notification system
├── .streamlit/config.toml         # Streamlit theme config
├── .streamlit/secrets.toml.template  # GSheets config template
├── Dockerfile            # Cloud Run deployment
├── Pipfile               # Python dependencies
├── requirements.txt      # pip-compatible dependencies
├── DOCUMENTATION.md      # Full user guide
└── README.md            # This file
```

## Technologies

- **Frontend**: Streamlit 1.40.0+
- **Data**: Pandas 2.0.0+, NumPy 1.24.0+
- **Viz**: Plotly 5.0.0+, Altair 5.0.0+
- **Auth**: Streamlit-Authenticator 0.3.0+
- **Cloud**: Google Sheets via gsheets-connection
- **Deployment**: Google Cloud Run

## Development

### Running Tests

```bash
# Lint code
pipenv run pylint app.py

# (No automated tests in v1.0.0)
```

### Code Style

- Python 3.11+ syntax
- Follow PEP 8 guidelines
- Use type hints where possible

## Roadmap (v1.1.0+)

- Baseline budgets with recurrence rules
- Automatic month generation from baselines
- Multi-user support (family/household budgets)
- Advanced reporting and export options
- Budget goal tracking

## Troubleshooting

**Issues?**
1. Check the About tab in the app
2. Read DOCUMENTATION.md for detailed guide
3. Check browser console for errors
4. Verify authentication credentials

**Data Loss?**
- Guest mode: Data is session-only and will be lost on browser close
- Use authenticated mode with Google Sheets for persistence

## License

[Include your license here]

## Support

- **Questions?** Read DOCUMENTATION.md
- **Found a bug?** Open an issue
- **Like it?** Support via the Donate tab!

---

**Version**: 1.0.0  
**Last Updated**: 2026-09-05  
**Status**: Production Ready