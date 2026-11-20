# Bataatas Business Management System — MKT322 CA-2

Streamlit + MySQL multi-branch management application extending the supplied CA-1 analysis dataset.

## Features

- Overview KPIs and Plotly charts by branch.
- Daily Sales: create, read, update and delete.
- Purchases: create, read, update and delete.
- Monthly P&L: create, read, update and delete.
- Branch directory: create, read and update; deletion is intentionally disabled to protect linked records.
- Parameterized SQL and calculated daily cash.

## Data note

The supplied project materials label the included data as synthetic/illustrative. The CSV files are the supplied CA-1 dataset, but do not describe them as actual confidential business records unless their provenance and permission have been verified.

## Local Windows setup

1. Install Python 3.10+ and MySQL 8+.
2. Import `bataatas_db_dump.sql` into MySQL Workbench. It drops/recreates the included tables, so back up any existing database first.
3. Edit `.streamlit/secrets.toml` and replace the password placeholder with the local MySQL password.
4. In PowerShell from this folder:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   streamlit run app.py
   ```

5. Open `http://localhost:8501`.

## Configuration

Local development reads `.streamlit/secrets.toml`. Cloud deployment reads environment variables first. Supported variables:

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- Railway MySQL variables: `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`

The included `secrets.toml` contains placeholders only. Never upload a real password to a public project.

## Hosting

Netlify Drop is not suitable for running this Streamlit server; it publishes static web build output. For a no-GitHub deployment, see `FRIEND_SETUP_AND_FACULTY_DEMO.md` for Railway CLI deployment from the local folder (`railway up`) with a Railway MySQL service. Hosting may incur charges; check the current provider pricing.

## Files

- `app.py` — Streamlit pages and UI.
- `db.py` — MySQL connection and query helpers.
- `bataatas_db_dump.sql` — schema and sample database records.
- `ca1_analysis_queries.sql` — CA-1 analysis queries.
- `clean_*.csv` — cleaned supplied CA-1 datasets.
- `.streamlit/secrets.toml` — local credential template; fill in locally and keep private.
- `FRIEND_SETUP_AND_FACULTY_DEMO.md` — step-by-step setup, hosting and presentation guide.
- `cleanup_test_records.sql` — preview and optional removal of the two known temporary test sales rows.

## Run

```bash
streamlit run app.py
```
