# Farm Fence Planner (NZD excl. GST)

Django 4.x web application to calculate farm fence material requirements and costs, export professional PDF/Excel reports, and manage regional pricing with optional scraping. Target region is Southland, New Zealand. All prices are NZD and exclude GST.

## Features
- Calculator for posts, wire, battens, labor, and costs
- Persisted calculations with detail view
- Exports: PDF (ReportLab) and Excel (openpyxl)
- Settings tab to manage materials, price sources, auto-update toggle, and "Scrape Now" placeholder
- Admin with actions and filters
- Hot wire support: specify number of hot wires (1-20) when top wire type is "Hot"
- Staples calculation: automatic staples for non-hot wires and netting, with configurable defaults
- Build rate (m/hr): customizable fence building speed (default 20 m/hr) for labor hour calculation

## Tech
- Django 4.x, SQLite (dev)
- Tailwind CSS via CDN (no build pipeline)
- ReportLab, openpyxl
- Optional scraping scaffold (requests/bs4 ready)

## Setup
1. Create and activate a virtualenv (Windows PowerShell):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Run migrations and seed demo data:
```
python manage.py makemigrations
python manage.py migrate
python manage.py seed_initial_data
```
4. Run the dev server:
```
python manage.py runserver
```
Open http://127.0.0.1:8000/ in your browser.

## Notes
- Currency: NZD, prices exclude GST.
- Region defaults: Southland. See `PriceSource` and `ScrapingSettings` models.
- Constants in `farm_fence_planner/settings.py`:
  - `LABOR_RATE_PER_HOUR = 55.0`
  - `WIRE_ROLL_LENGTH = 500`
  - `BUILD_RATE_METERS_PER_HOUR = 20`
  - Staples configuration:
    - `STAPLES_ENABLED = True`
    - `STAPLES_MATERIAL_NAME = 'U Staples (Box of 2000)'`
    - `STAPLES_PER_BOX = 2000`
    - `STAPLES_DEFAULT_PRICE = 183.99`
    - `STAPLES_PER_WIRE_PER_LINE_POST = 1`
    - `STAPLES_PER_WIRE_PER_END_POST = 2`
    - `STAPLES_PER_POST_FOR_NETTING = 4`

## Tests
Run unit and integration tests:
```
python manage.py test
```

## Disclaimer
All calculations and material prices provided by this application are indicative only and may change. Prices are sourced from suppliers and are subject to market fluctuations, regional variations, and supplier updates. Always verify current prices and requirements with your local suppliers before making purchasing decisions. The developers assume no liability for any discrepancies or decisions made based on the outputs of this tool.

## Future work
- Real supplier scraping adapters (e.g., Farmlands Invercargill) with retries and HTML fixtures
- Periodic scraping via `django-crontab` or Celery using `ScrapingSettings.default_scrape_interval_hours`
- Postgres + Docker for prod-like local dev
