# CellSentry — Architecture

A polished diagram is in [`architecture.svg`](architecture.svg) (use this in the deck).
The Mermaid version below renders directly on GitHub.

```mermaid
flowchart LR
  subgraph DATA["Data sources"]
    S1["Disruption signals<br/>news · sanctions · GDELT"]
    S2["Mineral shares<br/>USGS"]
    S3["Country-risk index"]
    S4["Cell-inspection lots<br/>incoming QC"]
  end

  subgraph CORE["Intelligence core"]
    EX["Extraction Agent · Claude<br/>event text → graph entities"]
    KG[("Knowledge Graph · Neo4j<br/>country→supplier→material→cell→pack→product")]
    RE["Risk &amp; Lead-time Engine · NetworkX<br/>concentration · geopolitical · events → propagation → lead-time"]
    PO["Scenario Orchestrator<br/>apply events · recompute · alerts"]
    BR["Briefing &amp; Mitigation Agent · Claude<br/>brief + recommendations"]
    QA["Quality &amp; Traceability<br/>SPC drift · cell→pack→VIN"]
    EV["Evaluation Harness<br/>lead-time · precision/recall"]
  end

  API["FastAPI<br/>/graph /events /scenario /quality /eval"]
  UI["Next.js War-Room<br/>signals · reactive graph · alerts"]

  S1 --> EX --> KG --> RE --> PO --> BR --> API
  S2 --> KG
  S3 --> RE
  S4 --> QA --> API
  EV --> API
  API --> UI
  UI -->|HTTP| API
```

## How it works

1. **Data sources** — live disruption signals (news / sanctions / GDELT), USGS mineral country-shares, a country-risk index, and incoming cell-inspection lots.
2. **Extraction Agent (Claude)** — turns free-text events into structured graph entities (materials, countries, suppliers) via forced tool-use; deterministic fallback when no API key.
3. **Knowledge Graph (Neo4j)** — the multi-tier battery supply chain (country → supplier → raw material → component → cell → pack → product), with in-memory fallback.
4. **Risk & Lead-time Engine (NetworkX)** — fuses concentration (HHI), geopolitical, and live event-boost risk, propagates it downstream along the BOM, and computes per-product **lead-time-to-impact** from inventory buffers.
5. **Scenario Orchestrator** — applies selected events, recomputes risk, and emits product alerts.
6. **Briefing & Mitigation Agent (Claude)** — writes the executive brief and recommended actions.
7. **Quality & Traceability** — SPC drift detection over inspection lots with cell→pack→VIN traceability.
8. **Evaluation Harness** — reproducible metrics (below).
9. **FastAPI → Next.js War-Room** — `/graph`, `/events`, `/scenario`, `/quality`, `/eval` power the 3-pane dashboard.

## Verified metrics (`python scripts/run_eval.py` · `GET /api/eval`)

| Metric | Result |
|---|---|
| Detection lead time | **median 19 days** (range 17–21) vs 0 reactive |
| Product attribution | precision / recall **1.0** |
| Quality defect detection (SPC) | **P 0.73 · R 1.0 · F1 0.84** |
