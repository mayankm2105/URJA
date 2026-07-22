# EV APM Agent Backend

This is the backend for the EV Asset Performance Management (APM) Agent. It monitors EV battery health, predicts Remaining Useful Life (RUL) using a validated formula, and generates maintenance recommendations via an LLM reasoning layer.

This backend is designed to be registered as one node in a LangGraph multi-agent orchestrator alongside three other independently-built agents. The FastAPI contract exposed here serves as the integration surface for that orchestrator.

## RUL Formula Note
The RUL formula used in this project was back-tested at MAE=11.1 cycles / RMSE=22.7 cycles / 80.2% within 20 cycles on real NASA battery data (1,415 rows, 34 batteries). The constants are intentionally fixed and documented in the code; they are not tuned live.

## Setup Instructions

### Environment Variables
1. Copy `.env.example` to `.env`.
2. Provide your `GROQ_API_KEY`.
3. Set your `DATABASE_URL` for PostgreSQL.

### Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Setup
1. Ensure PostgreSQL is running.
2. Create the database matching your `DATABASE_URL` (e.g., `ev_apm_db`).
3. Run the synthetic data generator and seed the DB:
```bash
python -m scripts.generate_synthetic_dataset
python -m app.data.seed_loader --csv scripts/synthetic_battery_dataset.csv
```

### Running the Server
```bash
uvicorn app.main:app --reload
```

### Running Tests
```bash
pytest -v
```
