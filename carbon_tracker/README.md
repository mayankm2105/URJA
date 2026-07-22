# CarbonPulse — Net Zero Carbon Intelligence Tracker

CarbonPulse is a unified, full-stack data analytics and intelligence suite for tracking carbon emissions, electrification pathways, and Net Zero trajectories for industrial EV fleets in India. 

The application is structured as a single-origin system: the FastAPI backend serves both the analytical JSON APIs and the dynamic glassmorphic frontend directly from port `8000`.

---

## 🚀 Quick Start (Run the App)

### Prerequisites
Make sure you have Python installed. The repository includes a pre-configured virtual environment (`venv`).

### Steps
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Activate the virtual environment:
   ```bash
   source ../venv/bin/activate
   ```
3. Start the application:
   ```bash
   python main.py
   ```
4. Access the dashboard in your browser:
   👉 **[http://localhost:8000/](http://localhost:8000/)**

---

## 🏗️ System Architecture

For a detailed breakdown of the system design, flowcharts, API data pathways, and carbon prioritization math models, refer to:
👉 **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)**

---

## 🛠️ Architecture & Tech Stack

### Backend (`/backend`)
* **Framework**: FastAPI (Python)
* **Server**: Uvicorn
* **Database**: SQLite (SQLAlchemy ORM)
* **APIs**:
  * `/api/dashboard` — Main KPI summaries and roadmap metrics.
  * `/api/emissions/timeseries` — Monthly Scope 1, Scope 3, and SBTi target points.
  * `/api/routes` — Geospatial telemetry details.
  * `/api/ai/priorities` — Heuristic-ranked fleet electrification recommendations.
  * `/api/ai/chat` — Context-aware advisor using Gemini API (with local rule-based fallback).

### Frontend (`/frontend`)
* **Design Language**: Dark Glassmorphism (authoritative sustainability theme).
* **Styling**: Tailwind CSS (custom design system configured with Stitch tokens in `DESIGN.md`).
* **Visualizations**:
  * **Charts**: Chart.js (custom gradients, line, and bar charts).
  * **Map**: Leaflet.js (custom dark satellite tiles, custom arc polylines, and pulsing telemetry rings).

---

## 📦 Database Schema & Models (`database.py`)

* **Fleet**: Tracks operator names, asset classes (mining, freight, last-mile), vehicle counts (diesel vs. EV), and individual target years.
* **Route**: Connects Indian cargo hubs (Mumbai, Delhi, Chennai, Jamshedpur, etc.) with coordinates, mileage, cargo payload, trip frequencies, and fuel-type emissions.
* **EmissionRecord**: Stores 30 months of historical telemetry records (Jan 2023 – Jun 2025) per fleet, containing Scope 1, Scope 3, EV-avoided metrics, and SBTi target pathways.
* **NetZeroCommitment**: Strategic corporate roadmap milestones.
* **Supplier**: Tracks battery minerals (Lithium, Cobalt) supply chain risk scores and carbon intensities.

---

## 🌿 Key Features

1. **Integrated Dashboard**: Real-time KPI summaries (EV penetration, YTD Scope 1/3, avoided tons) and live progress gauges.
2. **Emissions Intelligence**: Breakdown of Scope 1 direct diesel vs. Scope 3 upstream logistics, plus battery mineral supply-chain risk analysis.
3. **Geospatial Route Map**: Interactive map displaying telemetry routes in India. Colored lines indicate carbon intensity (Red: Critical, Amber: Attention, Green: Electrified).
4. **AI Carbon Advisor**: Live advice engine analyzing fleet database details. It identifies top electrification targets based on combined carbon impact and operational readiness index.
