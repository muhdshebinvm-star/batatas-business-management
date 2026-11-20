# Friend's setup guide and faculty demonstration

## Important project facts

- This is a Streamlit + MySQL application.
- The supplied README and app explicitly label the supplied data as synthetic/illustrative. Keep that disclosure unless the team has verified permission to replace it with real business records.
- The project contains `app.py`, `db.py`, `requirements.txt`, a MySQL dump, and cleaned CSV files.
- `.streamlit/secrets.toml` is included with placeholders only. Enter the password for the MySQL server on the computer where the app is being run.

## A. Run locally on Windows

1. Install Python 3.10 or newer and MySQL 8.
2. Open MySQL Workbench and connect to the local MySQL server.
3. Open `bataatas_db_dump.sql` in Workbench and execute it. This creates/populates `bataatas_db` and its tables. **It drops/recreates the tables in that database; back up any existing data first.**
4. Open this project folder in VS Code.
5. Open `.streamlit/secrets.toml` and replace `REPLACE_WITH_YOUR_LOCAL_MYSQL_PASSWORD` with the local MySQL root password. Save the file. Do not share this real password.
6. In VS Code Terminal, run:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   streamlit run app.py
   ```

7. Open the local URL printed in the terminal, usually `http://localhost:8501`.

If PowerShell blocks activation, run `python -m pip install -r requirements.txt` without activating the environment, then `python -m streamlit run app.py`.

## B. Hosting without GitHub: Railway local-folder deployment

Netlify's drag-and-drop deploy publishes web build output (HTML/CSS/JS/static assets); it does not run this long-lived Python Streamlit server. Do not upload this project to Netlify expecting the Streamlit application to start.

For a no-GitHub route, Railway supports uploading/deploying a local project folder with its CLI (`railway up`). It also provides a MySQL service. This route may require a paid plan/usage or payment method; check current pricing before proceeding.

1. Create/sign in to a Railway account.
2. Install Node.js if needed, then install the Railway CLI:

   ```powershell
   npm install -g @railway/cli
   ```

3. Open PowerShell in the project folder and run:

   ```powershell
   railway login
   railway init
   railway add --database mysql
   ```

   If the CLI command for adding a database is unavailable in the installed version, use the Railway dashboard to add a MySQL service to the same project.

4. In Railway, open the MySQL service and note its internal connection variables: `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, and `MYSQLDATABASE`.
5. Import `bataatas_db_dump.sql` into that hosted MySQL database. Use Railway's supported external TCP proxy connection or another MySQL client path. Do not use `localhost` for a cloud database.
6. Add a separate app service in the same Railway project and deploy the local project folder from PowerShell:

   ```powershell
   railway up
   ```

7. Ensure the app service can access the MySQL service variables. The updated `db.py` reads Railway's `MYSQL*` variables first, then local Streamlit secrets. If needed, add these variables to the app service by referencing the MySQL service's variables in Railway's Variables panel.
8. Generate a public domain for the app service in Railway's Networking/Settings panel.
9. Open the public URL and verify Overview, Daily Sales, Purchases, Monthly P&L, and Branches. Test with disposable records only.

Railway deployment is not complete until the database is imported, variables are connected, the service reports healthy, and the public URL works.

## C. What to show the faculty (5–7 minute demo)

1. **Project purpose (30 seconds):** Explain that the project extends the CA-1 data analysis into a multi-branch business management application.
2. **Architecture (45 seconds):** Explain: Streamlit UI -> Python `app.py` -> `db.py` connection helper -> MySQL database. The charts are produced with Plotly and tables with Pandas/Streamlit.
3. **Database (45 seconds):** In MySQL Workbench, show `bataatas_db` and the tables `branches`, `daily_sales`, `purchases`, and `monthly_pnl`.
4. **Overview (60 seconds):** Show KPIs, branch filter, sales trend and sales-by-branch chart. Explain that values come from MySQL records.
5. **Daily Sales CRUD (90 seconds):** Show records (Read), add a disposable record (Create), edit it (Update), then delete it with the confirmation checkbox (Delete). Explain cash calculation: total sales minus staff expense, rent/power and purchases.
6. **Purchases (60 seconds):** Show purchase ledger and demonstrate add/edit/delete with a disposable row.
7. **Monthly P&L and Branches (60 seconds):** Show P&L fields and branch directory; explain branch deletion is disabled to protect linked records.
8. **Hosting and documentation (30 seconds):** Show the hosted URL if deployment has succeeded, README setup steps, and explain where database credentials are stored.

## D. Questions the student should be ready to answer

- Why use MySQL? To persist relational business records across sessions.
- What does CRUD mean? Create, Read, Update, Delete.
- Why parameterized SQL? It keeps values separate from SQL text and reduces SQL-injection risk.
- What does `db.py` do? It centralizes database configuration, connection creation, queries and commits.
- How does the dashboard update? Streamlit reruns the app after form submission; the app reads the updated rows from MySQL.
- Why is branch deletion disabled? Sales, purchases and P&L rows reference branches through foreign keys.
- Where are credentials stored? Local `.streamlit/secrets.toml` or hosting environment variables/secrets, never in public source code.

## E. Before submission

- Verify the data provenance. The supplied app/README currently call the records synthetic/illustrative; do not claim they are real confidential business records unless independently verified and authorized.
- Remove temporary test rows after demonstrations.
- Do not publish the real `.streamlit/secrets.toml` or any password.
- Test all four CRUD operations for Daily Sales, Purchases and Monthly P&L; Branches supports create/read/update and intentionally no delete.
- Keep screenshots of the app, database tables, CRUD tests, and successful hosted URL.
