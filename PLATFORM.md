# Urja — Platform Architecture

Urja is **one application**: a single Next.js UI in which every module is a
first-class view sharing one design system (palette, typography, layout
primitives, chart styling), backed by four independent module services.

## Composition

```
                 ┌────────────────────────────────────────────────────┐
                 │        Urja UI · Next.js · :3000                 │
                 │  one shell · one design system · one nav            │
                 │                                                     │
                 │  Overview │ Supply │ Fleet │ Electrify │ Guardian │ │
                 │           │ Carbon │ Validation                     │
                 └──────┬──────────┬──────────┬──────────┬────────────┘
                        │          │          │          │
                  CellSentry   FleetMind  CarbonPulse  Fleet Guardian
                  API :8001    API :8002  API :8003    API :8004
                  (Neo4j/mem)  (NumPy)    (SQLite+     (SQLite+Groq)
                                           Gemini)
```

## The views

| Route | Module behind it | What it shows |
| --- | --- | --- |
| `/` | all four | Platform overview — live KPIs pulled from every service, lifecycle narrative |
| `/supply` | CellSentry | Disruption signals · force-graph risk propagation · scenario alerts with lead time |
| `/fleet` | FleetMind | Worst-first battery health board · SoH/RUL trajectory · fade attribution · maintenance queue |
| `/electrify` | FleetMind | India electrification readiness index · EV procurement recommendations (INR) |
| `/guardian` | Fleet Guardian | Cycle-level battery APM — RUL with confidence bands, temperature/voltage anomalies, LLM maintenance reasoning |
| `/charging` | FleetMind | Depot charging: energy needed vs actually delivered at observed charger uptime · N-1 contingency · coupled to the repair queue |
| `/quality` | CellSentry | SPC control chart over incoming cell batches · flagged lots with plain-English reasons · cell→pack→VIN traceability |
| `/carbon` | CarbonPulse | Scope 1/3 vs SBTi target trajectory · AI electrification priorities · top-emitting routes |
| `/proof` | all four | Every accuracy claim in one place, plus the gaps we haven't closed |
| `/validation` | FleetMind | NASA real-cell validation of the degradation models |

## How the single design language is achieved

- **CellSentry & FleetMind** were already built on the same design tokens
  (navy `#0b1020`/`#0f1530`, health/risk triad `#10b981`/`#ee9800`/`#ff5d52`),
  so their React components were ported into `platform-new/` directly —
  CellSentry's styles scoped under `.supply` to avoid class collisions.
- **CarbonPulse** (originally a standalone glassmorphic HTML page) and
  **Fleet Guardian** (originally a Vite+Tailwind app) got **native views
  rebuilt in the shared design system** over their untouched backend APIs —
  same KPI tiles, panel styles, rank rows, tables and recharts styling as the
  rest of the platform.
- One `globals.css` defines the tokens once; every view consumes them.

## Services (unchanged module backends)

| Service | Port | Stack | Env wiring from the launcher |
| --- | --- | --- | --- |
| CellSentry | 8001 | FastAPI + Neo4j (in-memory fallback) | `CORS_ORIGINS=http://localhost:3000` |
| FleetMind | 8002 | FastAPI + NumPy | `CORS_ORIGINS=http://localhost:3000` |
| CarbonPulse | 8003 | FastAPI + SQLite (+ Gemini) | `PORT=8003`, `ALLOWED_ORIGINS` |
| Fleet Guardian | 8004 | FastAPI + SQLite (+ Groq) | `DATABASE_URL=sqlite+aiosqlite:///./test.db`, `GROQ_API_KEY` |

The UI reads per-module bases from `NEXT_PUBLIC_SUPPLY_API` /
`NEXT_PUBLIC_FLEET_API` / `NEXT_PUBLIC_CARBON_API` / `NEXT_PUBLIC_GUARDIAN_API`
(defaults match the launcher's ports).

Everything is started by [`run_platform.sh`](run_platform.sh); one-time deps by
[`setup.sh`](setup.sh).

## Module code changes (kept minimal & non-invasive)

- `carbon_tracker`: hardcoded port → `PORT` env; requirements exact-pins →
  floors (Python 3.14 wheel availability). Its original standalone UI still
  works at `:8003`.
- `fleet_guardian`, `cellsentry`, `fleetmind`: **zero backend changes**.
- Original per-module frontends remain in their directories and still run
  standalone; the platform app supersedes them for the integrated demo.

## Extending

Add a module by: (1) giving its API a port in `run_platform.sh`, (2) adding a
typed client in `platform-new/lib/<module>.ts`, (3) building its view with the
shared primitives (`.panel`, `.tile`, `.asset-card`, `.queue`, `.val-stats`),
and (4) adding a nav tab + overview card.


## Evidence against PS3's evaluation focus

PS3 names five evaluation criteria. Where each is proved, and how:

| PS3 metric | Result | Source |
| --- | --- | --- |
| Battery degradation accuracy vs observed | SoH MAE 0.08 pp synthetic; **2.0% fit / 3.4 pp forecast / 21-cycle RUL on real NASA cells**. Guardian's independent backtest: **1.43-cycle MAE, 100% within 20** | `/proof`, `/validation` |
| Supply-chain risk detection lead time | **19 days median** across 11 real 2023–25 events (reactive baseline = 0) | `/proof`, `/supply` |
| Quality defect precision/recall | **P 0.73 / R 1.00 / F1 0.84** over 90 inspection lots, non-tautological (detector sees observed value, ground truth is the hidden process value) | `/proof`, `/quality` |
| Readiness scoring vs expert baseline | **90% verdict agreement, Cohen's kappa 0.839, Spearman rho 0.879** vs a hand-labelled expert baseline that reasons hard-gates-first (a deliberately different process from the engine's weighted average) | `/proof`, `/electrify` |
| Carbon accuracy vs measured emissions | **7.5% fleet-wide, 11.4% MAPE per route** vs metered litres. Validates the km/L assumption (the factor 2.68 kg/L is a published constant, not a modelling choice) | `/proof`, `/carbon` |

### Coverage of PS3's six illustrative build areas
1. EV Asset Performance Management — **two** independent implementations (FleetMind + Guardian)
2. Fleet Electrification Readiness & Procurement — FleetMind (India EV catalog, INR, lead times)
3. EV Supply Chain Risk & Traceability — CellSentry
4. Manufacturing Quality Intelligence (QMS/SPC) — CellSentry, surfaced at `/quality`
5. Net Zero Progress & Carbon Intelligence — CarbonPulse
6. Maintenance Operations Optimiser — workshop bays + parts lead **and** charging-infrastructure uptime, planned together (`/charging`)


## What the evaluation found (and we did not hide)

Building the evals surfaced three real defects. All are fixed or stated in-product:

1. **Compensatory scoring recommended an infeasible vehicle.** The readiness index
   is a weighted average, so strong TCO offset a zero range score — it suggested a
   180 km bus for a 245 km route. Fixed with a `range_feasible` hard gate +
   `feasibility_note` shown in the UI. The expert-agreement metrics were verified
   unchanged after the fix (90 / 0.839 / 0.879), so the product improved without
   gaming the score.
2. **Carbon under-reports on hills.** The fuel model uses payload alone, so it
   misses terrain and congestion: up to **28% under** on ghat corridors like
   Mumbai→Pune, **7.5% under** fleet-wide. Surfaced on `/carbon`, not buried.
3. **No charging redundancy.** N-1 contingency shows all five depots run a single
   charger — one failure stops that depot's fleet. Invisible in headroom numbers,
   which all look comfortable.

### Honest limitations, stated in-product
- The expert baseline is one practitioner's judgement, not blind multi-expert
  elicitation.
- Fuel-meter readings are simulated from published Indian economy ranges, not a
  live telematics feed. (The NASA battery cells, by contrast, are genuinely real.)
- Guardian's backtest number is a committed constant — it exposes no endpoint —
  and `/proof` says so rather than implying it is live.
