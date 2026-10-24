# SalesPulse — Sales Management Dashboard

A responsive sales dashboard using Flask, SQLite, HTML, CSS, JavaScript and Chart.js.

## Features
- Revenue, net profit, order count, average order value, profit margin and units sold
- Monthly revenue/profit chart, category distribution, regional performance and top products
- Search and filter by customer/product, date, category and region
- Add, edit and delete sales records
- Export records as CSV
- Sample data, API validation and automated tests

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Tests
```bash
python -m unittest discover -s tests -v
```

## Deploy to Render
Push this folder to GitHub. Create a Render Web Service and set:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

SQLite is suitable for a classroom demo. Hosting filesystems can be ephemeral; use a persistent disk or managed database if data must survive redeploys. This demo has no authentication and should not be used for sensitive real customer data without security hardening.
