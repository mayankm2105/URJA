# FleetMind — Build Status

## W1 — Vertical slice (battery SoH / RUL core) ✅ complete & verified

**Goal:** end-to-end slice proving the intellectual core — predict per-asset
battery State-of-Health and remaining-useful-life from observed telemetry, with
honest accuracy numbers.

Built & verified (backend, headless + TestClient):

- **Degradation model** (`app/soh/degradation.py`) — semi-empirical Li-ion fade:
  `loss = b_cyc·stress·√EFC + b_cal·stress·√days`, with Arrhenius temperature,
  DoD and C-rate stress factors; per-chemistry coefficients (NMC ~1.5k EFC, LFP
  ~3.5k EFC to the 80% knee).
- **Synthetic-but-physical fleet** (`app/data/fleet.py`) — 10 diverse assets
  (e-bus / e-van / e-rickshaw, NMC & LFP, hot/temperate, light/heavy duty),
  weekly capacity samples + realistic BMS noise. **CRC32-seeded → byte-identical
  across runs** (eval numbers reproducible).
- **Estimator** (`app/soh/estimator.py`) — one-parameter least-squares fit of the
  fade curve to observed BMS data. (Cycle vs calendar are collinear within a
  single constant-duty asset; separating them is a W2 fleet-pooled-fit task.)
- **RUL projection** (`app/soh/rul.py`) — bisection to the 80% knee → days/EFC
  remaining + health band; forward projection series for charting.
- **Asset-health agent** (`app/agents/health_brief.py`) — Claude exec brief +
  physics-derived maintenance recs, deterministic fallback when no API key.
- **Eval harness** (`app/eval/harness.py`) — temporal holdout vs ground truth.
- **API** (`app/api/routes.py`) — `/health`, `/fleet`, `/asset/{id}`, `/eval`.

**Verified results (reproducible):**

| Metric | Value |
| --- | --- |
| SoH MAE (holdout) | 0.089 pp |
| SoH RMSE | ~0.10 pp |
| RUL median abs error | ~17 days |
| RUL MAPE | ~2.5% |
| Fleet | 10 assets · avg SoH 75.1% · 9 at-risk · 5 end-of-life |

All endpoints pass via FastAPI `TestClient`; `demo.py` and `run_eval.py` run
headless with no API key.

## W2 — Model depth ✅ complete & verified

- **Fleet-pooled fit** (`app/soh/pooled.py`) — pools observations across assets of
  a chemistry and regresses `1-SoH = b_cyc·stress·√EFC + b_cal·stress·√days` with
  per-asset stress factors from telematics. Differing duty cycles break the
  single-asset collinearity, making `b_cyc`/`b_cal` separately identifiable. The
  per-asset capacity-loss split shown in the API is now **data-derived** from these
  coefficients (not the ground-truth physics).
- **Coefficient-recovery eval** (`app/eval/harness.py`) — validates the pooled fit
  against the generating coefficients: **max 2.7%, mean 1.4% relative error**
  (NMC b_cyc 0.3% / b_cal 1.6%; LFP b_cyc 0.9% / b_cal 2.7%).
- **Predictive-maintenance scheduler** (`app/ops/schedule.py`) — RUL-driven,
  downtime-aware work-order queue: parallel service bays + parts lead time,
  worst-first sequencing, `overdue` flag when a swap can't complete before the EoL
  knee. Tunable via `?bays=&parts_lead_days=`. Current fleet: 6 scheduled, 5
  overdue, queue clears day 48 (1 bay / 30-day lead) → day 30 (2 bays / 21-day lead).
- **Maintenance agent** (`app/agents/maintenance.py`) — Claude ops narrative over
  the queue with deterministic fallback.
- **New endpoints** — `/api/maintenance`, `/api/model`; eval now includes
  `coefficient_recovery`. New script `scripts/run_maintenance.py`.
- **Real-data seam** — data layer isolated behind `fleet.py`'s `observed_series` /
  `current_state` contract; NASA / Severson adapters are a drop-in (documented, not
  yet wired — synthetic data is already physically grounded).

## W3 — War-room dashboard ✅ complete & verified

Next.js three-pane dashboard (`frontend/`), responsive so the trajectory chart is
never crushed. Fleet health board (worst-first, color-coded bands) · asset detail
(recharts SoH trajectory: observed history + dashed forward projection to the red
80% knee, RUL/SoH/EFC tiles, dominant driver, pooled cycle/calendar attribution
bar) · brief + predictive-maintenance queue. Typed client over `/fleet`,
`/asset/{id}`, `/maintenance`. Verified in-browser (live data, selection updates
chart+brief+attribution, no console errors); `next build` passes. Design built on
the CellSentry Stitch-derived tokens (Stitch generation timed out without
returning a screen).

## W4 (in progress) — Real-data validation ✅

Upgraded the estimator to a 2-mechanism model `loss = a·√EFC + c·EFC` (SEI √-fade +
linear late-life wear-out). It generalises: synthetic `c ≈ 0` (pure √ as generated,
SoH MAE 0.08pp / RUL MAPE 2.5% preserved), real NASA `c` activates for the knee.

- **NASA adapter** (`app/data/nasa.py` + committed `nasa_capacity.csv`, 636 rows
  extracted from the public NASA battery aging dataset) feeds real cells through
  the identical estimator/RUL pipeline.
- **Validation harness** (`app/eval/nasa_eval.py`): model adequacy (full-trajectory
  in-sample RMSE **mean 1.8% / max 2.0% SoH**) + knee-onset forecast (**SoH MAE
  3.4pp**, **RUL median ~21 cycles**). Endpoints `/api/validation`,
  `/api/validation/cells`; script `scripts/run_validation.py`.

### W4 UI + deliverables ✅

- **Validation view in the dashboard** — Fleet/Validation toggle in the top bar;
  the Validation view shows real-data proof: stat cards (cells, model-fit RMSE,
  knee-onset SoH MAE, RUL error), a NASA multi-cell capacity-fade chart with the
  80% knee line, and a per-cell forecast table (true vs predicted end-of-life
  cycle). Verified in-browser.
- **Architecture diagram** — `docs/architecture.svg` + `docs/ARCHITECTURE.md`.
- **Demo script / storyboard** — `docs/DEMO.md` (shot-by-shot, tied to judging
  criteria).

## Next

- Pitch deck (deferred by request).
- Demo video recording (script ready in `docs/DEMO.md`).
- Optional features: richer telematics, second-life routing, carbon-per-route
  tracking.
- Push to GitHub when ready (all commits currently local-only).
