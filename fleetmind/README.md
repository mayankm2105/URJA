# FleetMind — EV Battery Asset Performance & RUL Intelligence

**ET AI Hackathon 2026 · Problem Statement 3 (Industrial EV Supply Chain & Asset Intelligence).**
FleetMind is the **fleet-operator** module of the platform: it turns raw battery
telemetry into per-asset **State-of-Health (SoH)**, **remaining-useful-life (RUL)**
predictions, and prioritised **predictive-maintenance** actions for an EV fleet.
(Sibling module: **CellSentry**, the upstream supply-chain risk & traceability engine.)

## What it does

- **Battery health board** — every asset ranked worst-first by current SoH, with
  its health band (`healthy` / `aging` / `end_of_life`), projected RUL, and the
  dominant physical fade driver (heat, fast-charging, deep discharge, throughput).
- **Degradation engine** — a semi-empirical Li-ion model (sqrt-of-throughput SEI
  ageing + calendar ageing, accelerated by Arrhenius temperature, depth-of-discharge
  and C-rate stress factors) grounded in published aging literature. Per-asset
  coefficients are fit to observed BMS capacity readings by least squares.
- **Fleet-pooled fit** — a single asset can't separate cycle from calendar ageing
  (they're collinear at constant duty). Pooling assets with *different* duty cycles
  breaks the degeneracy and **recovers the physical coefficients to within ~3% of
  ground truth**, enabling a data-derived cycle-vs-calendar split of every asset's
  capacity loss.
- **RUL projection** — extrapolates the fitted curve forward to the 80%
  end-of-life knee, giving days-to-replacement per asset.
- **Predictive-maintenance scheduler** — turns RUL projections into a prioritised,
  downtime-aware service queue (parallel bays, parts lead time), flagging assets
  that can't be serviced before failure and quantifying the lead time that early
  prediction removes from the critical path.
- **Agents** — Claude writes an executive asset-health brief and a maintenance ops
  plan; the engine derives physics-based recommendations (deterministic fallback so
  the whole API runs with **zero external dependencies / no API key**).
- **Real-data validation** — the *same* model/estimator validated on the public
  **NASA battery aging dataset** (real cells B0005/6/7/18), proving the approach
  holds on real degradation, not just synthetic data.
- **Evaluation harness** — honest temporal-holdout accuracy against ground-truth
  degradation trajectories (see numbers below).

## Degradation model

Capacity loss is fit as a two-mechanism curve:

```
1 - SoH = a·√EFC + c·EFC          (early-life SEI √-fade + late-life linear wear-out)
```

It generalises cleanly: on the clean synthetic fleet the linear term collapses to
`c ≈ 0` (pure √, as generated); on the real NASA cells `c` activates to capture the
late-life "knee" that a pure-√ model under-predicts.

## Headline metrics (reproducible)

**Synthetic fleet** (`python scripts/run_eval.py`, temporal holdout):

| Metric | Value |
| --- | --- |
| SoH prediction MAE / RMSE | **0.08 / 0.10 pp** |
| RUL median absolute percentage error | **2.5%** |
| Pooled cycle/calendar coefficient recovery error | **max 2.7%, mean 1.4%** |

**Real NASA cells** (`python scripts/run_validation.py`):

| Metric | Value |
| --- | --- |
| Model adequacy — full-trajectory in-sample RMSE | **mean 1.8% / max 2.0% SoH** |
| Knee-onset SoH forecast MAE | **3.4 pp** |
| Knee-onset RUL forecast error (cycles-to-80%) | **median ~21 cycles** |

## Architecture

Full diagram and component walkthrough: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
Demo script: [docs/DEMO.md](docs/DEMO.md).

```
backend/  FastAPI
  app/
    soh/        degradation model · estimator · pooled fleet fit · RUL projection · service layer
    data/       synthetic-but-physical EV fleet + NASA real-cell adapter (nasa_capacity.csv)
    ops/        predictive-maintenance scheduler (downtime-aware work-order queue)
    agents/     Claude asset-health + maintenance agents (+ deterministic fallback)
    eval/       synthetic harness (SoH · RUL · coeff recovery) + NASA real-data validation
    api/        /health · /fleet · /asset/{id} · /maintenance · /model · /eval · /validation
  scripts/      demo.py · run_eval.py · run_maintenance.py · run_validation.py
frontend/  Next.js war-room dashboard (W3)
```

The operational fleet is **synthetic but physical** (trajectories from the same
degradation model, parameterised to real NMC/LFP fade rates). The data layer is
isolated behind an `observed_series` contract, so real datasets drop in as
adapters — `app/data/nasa.py` does exactly this for the NASA battery aging
dataset, feeding the identical estimator/RUL pipeline for external validation.

## Run it

```bash
cd backend
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt

# headless proofs
./.venv/bin/python scripts/demo.py            # fleet health board + worst-asset drill-down
./.venv/bin/python scripts/run_eval.py        # synthetic degradation-prediction accuracy
./.venv/bin/python scripts/run_maintenance.py # predictive-maintenance service queue
./.venv/bin/python scripts/run_validation.py  # real-data validation on NASA cells

# API
./.venv/bin/uvicorn app.main:app --reload --port 8000
#   GET /api/fleet            fleet health board
#   GET /api/asset/{id}       per-asset history + projection + recommendations
#   GET /api/asset/{id}?brief=true   include the LLM health brief
#   GET /api/maintenance      predictive-maintenance work-order queue (?bays=&parts_lead_days=&plan=)
#   GET /api/model            fleet-pooled cycle/calendar coefficients
#   GET /api/eval             synthetic accuracy metrics (SoH · RUL · coefficient recovery)
#   GET /api/validation       real-data validation on the NASA battery aging dataset
```

Set `ANTHROPIC_API_KEY` in `backend/.env` to enable live Claude health briefs
(`claude-opus-4-8` by default; set `BRIEFING_MODEL=claude-haiku-4-5` to cut cost).

## Data & attribution

Real validation data is the **NASA Prognostics Center of Excellence "Battery
Aging" dataset** (cells B0005/B0006/B0007/B0018; B. Saha & K. Goebel, NASA Ames
Prognostics Data Repository — public domain US Government work). The repo ships a
compact per-cycle discharge-capacity extract (`backend/app/data/nasa_capacity.csv`).
The operational fleet data is synthetic, generated by the degradation model.

## Status

W1–W4 complete & verified (battery SoH/RUL core · fleet-pooled separation ·
predictive maintenance · war-room dashboard · real-data validation + UI ·
architecture diagram · demo script) — see [STATUS.md](STATUS.md).
