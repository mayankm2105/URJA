# Fleet Guardian - EV Asset Performance Management (APM)

Fleet Guardian is a prototype for an EV Asset Performance Management platform. It is designed to monitor electric vehicle battery health, predict Remaining Useful Life (RUL), and provide maintenance recommendations using an LLM reasoning layer. 

This repository contains both the frontend and backend applications for the prototype.

## Project Structure

- **`Fleet-Guardian-Backend/`**: A FastAPI-based Python backend that exposes endpoints for battery health monitoring, synthetic data generation, and LLM-driven maintenance recommendations.
- **`Fleet-Guardian-Frontend/`**: A React application built with Vite and Tailwind CSS, offering a dashboard interface for fleet operators to visualize asset health.

---

## ⚙️ Backend Setup & Usage

The backend evaluates battery metrics and predicts RUL based on a validated formula.

### Requirements
- Python 3.9+
- PostgreSQL

### Installation

1. Navigate to the backend directory:
   ```bash
   cd Fleet-Guardian-Backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your `GROQ_API_KEY`
   - Set up your `DATABASE_URL` (e.g., pointing to your local PostgreSQL instance)

### Database Seeding
Ensure PostgreSQL is running, then run the synthetic data generation and seeding scripts:
```bash
python -m scripts.generate_synthetic_dataset
python -m app.data.seed_loader --csv scripts/synthetic_battery_dataset.csv
```

### Running the Server
Start the FastAPI server on port 8000:
```bash
uvicorn app.main:app --reload
```
The API documentation will be available at `http://localhost:8000/docs`.

---

## 🖥️ Frontend Setup & Usage

The frontend provides a real-time dashboard for operators to monitor the EV fleet's status.

### Requirements
- Node.js (v18+) or Bun

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd Fleet-Guardian-Frontend
   ```
2. Install dependencies (using npm, yarn, or bun):
   ```bash
   npm install
   # or
   bun install
   ```

### Running the Development Server
Start the Vite development server:
```bash
npm run dev
# or
bun run dev
```
The frontend application will be available at the URL provided in your terminal (usually `http://localhost:5173`).

---

## Architecture Note
The backend is designed to be registered as one node in a LangGraph multi-agent orchestrator. The FastAPI contract exposed serves as the integration surface for that orchestrator.
