# CellSentry — Project Status

**Agentic early-warning system for EV battery supply chains.** It maps a battery
supply chain across every tier (cell → cathode/anode → Li/Co/Ni/graphite →
mine/country), fuses live geopolitical + ESG signals onto that graph, and tells
you **which products are at risk, why, and how many days before it hits the
line.**

- **Hackathon:** ET AI Hackathon 2026 — **Problem Statement 3** (AI for Industrial EV Supply Chain & Asset Intelligence), *Supply-Chain Risk & Traceability* angle.
- **Repo:** https://github.com/De-Coder05/cellsentry (private)
- **Timeline:** ~1 month · **Status date:** 2026-06-26

---

## TL;DR for the team

- **Where we are:** Week 1 ✅ · Week 2 ✅ · Week 3 ✅ · **Week 4 (proof + submission) = next**.
- **~75% of the timeline done — the risk engine, the Claude agents, and the war-room UI are all built and working.** What remains is the evaluation harness (real metrics) and submission assets (deck, architecture diagram, demo video).
- **It works today.** A China-graphite-export signal flows through the graph and flags both EV products with a **21-day lead time**, a full risk path, an exec brief, and mitigation actions — verified end-to-end on a live Neo4j cloud DB.
- **You can run it in ~3 minutes with zero infrastructure** (in-memory fallback, no database or API key needed) — see *Run it locally* below.

---

## The plan (4-week roadmap)

| Week | Goal | Status |
|---|---|---|
| **W1** | End-to-end vertical slice: graph → risk → API → graph UI | ✅ **Done & verified** |
| **W2** | Composite risk engine + lead-time + Claude agents (the "brain") | ✅ **Done & verified** |
| **W3** | Next.js "war-room" UI: signal feed, live graph reaction, alert panel | ✅ **Done** (designed in Stitch, built in Next.js) |
| **W4** | Quality+traceability module, compliance/RAG, **evaluation harness** (real metrics), pitch deck, architecture diagram, demo video | ⏳ Pending |

**Deliverables required:** working prototype · architecture diagram · pitch deck · demo video.
**Judging:** Innovation 25% · Business Impact 25% · Technical Excellence 20% · Scalability 15% · UX 15%.

---

## What's built & verified

### Week 1 — vertical slice ✅
- **FastAPI** backend + **Neo4j (Aura cloud)** graph store with an **automatic in-memory fallback** (runs with zero infra).
- Multi-tier **knowledge graph** of a battery supply chain, seeded with real companies, countries, and USGS-grounded mineral country-shares.
- **HHI concentration risk** computed per node and propagated to the product.
- **Next.js + react-force-graph** UI rendering the graph with a risk color overlay.

### Week 2 — the intelligence ✅
- **Composite risk engine** — fuses three dimensions and propagates them downstream through the bill-of-materials graph:
  - *Concentration* (HHI over a material's global country shares)
  - *Geopolitical* (per-country risk baseline)
  - *Event boosts* (live disruption signals)
  - → plus **per-product lead-time-to-impact** computed from inventory buffers along the path.
- **14-event curated corpus** of real 2023–25 events (China graphite controls, DRC cobalt export suspension, Indonesia nickel policy, EU Battery Regulation, Chile lithium, US tariffs, …), each with ground-truth labels.
- **Multi-agent layer (Claude)** — *extraction agent* (maps free-text events to graph entities via forced tool-use), *briefing agent* (writes the exec brief + recommendations), and a *scenario pipeline* orchestrator. **Deterministic fallback** so the whole thing runs even without an API key.
- **Two products** (NMC E-Scooter + LFP E-Rickshaw) sharing a graphite anode — enables the differential-impact story.
- **New API:** `GET /api/events`, `POST /api/scenario`.

### Verified results (these are our proof points for the deck)

| Scenario | Result |
|---|---|
| 🇨🇳 China graphite export control | E-Scooter **63 → 88**, E-Rickshaw **60 → 89** · both **~21-day lead time** (shared anode) |
| 🇨🇩 DRC cobalt export suspension | **Only** E-Scooter 63 → 70 (19-day lead) — the LFP rickshaw is untouched (no cobalt) ✅ |
| Both events together | Scooter lead time correctly tightens to 19 days (nearer shock wins) |

Graph today: **30 nodes / 34 edges**, 2 products, 10 suppliers across 3 tiers, 5 raw materials.

---

## How it works (architecture)

```
 Next.js + react-force-graph (war-room UI)        ← W3 builds this out
            │  HTTP
            ▼
 FastAPI backend
   ├─ /api/graph      baseline supply graph + composite risk
   ├─ /api/events     curated disruption-signal corpus
   └─ /api/scenario   apply events → risk + lead-time → alerts + briefs
            │
   ┌────────┴───────────────────────────────┐
   │  Risk engine (NetworkX)                 │  concentration + geopolitical
   │   + lead-time-to-impact                 │  + event boosts, propagated
   ├─ Multi-agent layer (Claude)            │  extraction · briefing · pipeline
   └─ Graph store                           │
        ├─ Neo4j (Aura cloud)   ← primary
        └─ in-memory            ← auto fallback (zero infra)
```

**The core idea (one sentence for the pitch):** a disruption signal raises the
risk of the specific material it hits, that risk *propagates downstream* through
the bill-of-materials to the finished product, and the inventory buffers along
that path give us the **lead time** — i.e. how long until it actually stops the line.

**Risk model dimensions:** concentration (HHI), geopolitical (country risk),
live event boosts → combined per node, then propagated with a weakest-link bias.

---

## Tech stack

- **Backend:** Python · FastAPI · NetworkX (graph math) · Neo4j driver
- **Graph DB:** Neo4j Aura (free tier) — with in-memory fallback
- **AI:** Claude (`claude-opus-4-8` default; configurable) via the Anthropic SDK
- **Frontend:** Next.js 14 (TypeScript) · react-force-graph
- **Planned (W4):** Chroma (RAG over EU Battery Regulation), SPC/ML for the quality module

---

## Run it locally (teammates start here)

**Zero-infra path — no database, no API key needed** (uses the in-memory fallback):

```bash
git clone https://github.com/De-Coder05/cellsentry.git
cd cellsentry/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/demo_graphite.py          # see the graphite scenario in your terminal
uvicorn app.main:app --reload --port 8000   # API at http://localhost:8000
```

Frontend (separate terminal):
```bash
cd cellsentry/frontend
npm install
npm run dev                               # http://localhost:3000
```

**Optional upgrades:** copy `backend/.env.example` → `backend/.env` and add
`NEO4J_URI`/`NEO4J_PASSWORD` (free Neo4j Aura instance) to use the cloud graph,
and/or `ANTHROPIC_API_KEY` to switch the agents from the deterministic fallback
to live Claude.

Quick API check once the server is up:
```bash
curl -s -X POST localhost:8000/api/scenario \
  -H 'Content-Type: application/json' \
  -d '{"event_ids":["graphite-china-export-2023"]}'
```

---

## What's left

### Week 3 — the war-room UI ✅ (done)
Three-pane dashboard: signal feed → click an event → the supply graph reacts
live (hit nodes glow red, the risk path animates) → alert panel (affected
products, risk delta, lead time, brief, recommended actions). Designed in
Google Stitch, built in Next.js + react-force-graph against the live API.

### Week 4 — depth, proof & polish
- **Quality + traceability** module (cell → pack → vehicle).
- **Compliance / RAG** over the EU Battery Regulation.
- **Evaluation harness** → real numbers for the deck (detection lead time, precision/recall).
- Architecture diagram · pitch deck · demo video · rehearsal.

### Where teammates can plug in
- **Frontend (React/Next):** owns Week 3 — the highest-visibility piece.
- **Data/ML:** the Week-4 quality module + evaluation harness.
- **Pitch/design:** start the deck narrative now using the verified results above.
- **Domain research:** expand the supply graph (more suppliers/materials/products) and the event corpus.

---

*Single source of truth for status. Update as weeks complete.*
