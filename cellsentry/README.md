# CellSentry

**Agentic early-warning system for EV battery supply chains.** Maps a battery
supply chain across all tiers (cell → cathode/anode → Li/Co/Ni/graphite →
mine/country), fuses geopolitical, quality and ESG signals onto that graph, and
flags which products are at risk, why, and how many days before it hits the line.

> ET AI Hackathon 2026 · Problem Statement 3 — *Supply-Chain Risk & Traceability* angle.

## Status: Week 1 — vertical slice

End-to-end skeleton: seed knowledge graph → risk engine (HHI concentration,
propagated downstream) → API → Next.js force-graph with a risk overlay.

## Architecture

```
frontend (Next.js + react-force-graph)  ──HTTP──>  backend (FastAPI)
                                                     ├─ risk engine (NetworkX)
                                                     └─ graph store
                                                          ├─ Neo4j (Aura)   ← primary
                                                          └─ in-memory      ← auto fallback
```

The graph store is Neo4j-first with an automatic in-memory fallback: if
`NEO4J_URI` is not set, it runs in-memory so you can develop without a database.

## Run it

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # optional; runs in-memory without it
uvicorn app.main:app --reload --port 8000
```

Check: http://localhost:8000/api/health and http://localhost:8000/api/graph

### Connect Neo4j Aura (optional this week, needed for scale)

1. Create a free instance at https://neo4j.com/cloud/aura-free/
2. Download the credentials file; paste `NEO4J_URI` and `NEO4J_PASSWORD` into `backend/.env`
3. Load the seed: `cd backend && python scripts/load_seed.py`

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open http://localhost:3000 — graphite and cobalt should show red (high
concentration), the e-scooter product amber.

## Roadmap

- **W1** vertical slice (this) ✅
- **W2** full risk model + graph propagation + lead-time; signal ingestion &
  extraction agent (Claude); mitigation/briefing agent
- **W3** Next.js war-room UI (heatmap, alert feed, drill-down risk path)
- **W4** quality + traceability module; compliance/RAG; evaluation harness
  (lead-time & precision/recall); deck, architecture diagram, demo video
