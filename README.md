# SmartPlate AI — Backend

FastAPI + PostgreSQL backend for SmartPlate AI, a food waste intelligence system for college canteens. Tracks meal preparation, consumption, and waste, and powers demand forecasting, waste analytics, real-time alerts, and menu planning.

## Tech Stack
- FastAPI
- PostgreSQL (hosted on Neon)
- SQLAlchemy ORM

## Setup
git clone <this-repo-url>
cd smartplate-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

Create a `.env` file with:
DATABASE_URL=your_postgresql_connection_string

Run the server:
uvicorn main:app

API docs available at http://127.0.0.1:8000/docs

## Endpoints
- `/menu` — manage menu items
- `/sessions` — meal sessions (date + meal type)
- `/prep` — food preparation records
- `/consumption` — consumption & waste records
- `/predictions` — demand predictions (placeholder, pending ML model integration)
- `/analytics/summary` — dashboard summary stats
- `/analytics/weekly-demand` — actual vs predicted demand by day
- `/alerts` — waste anomaly alerts
- `/menu-planner` — editable production planning per dish