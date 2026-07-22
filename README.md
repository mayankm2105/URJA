# Urja - Industrial EV Intelligence Platform

**ET AI Hackathon 2026 · PS3 — AI for Industrial EV Supply Chain & Asset Intelligence · Accelerating Net Zero.**

Urja unifies four specialist modules into one command centre spanning the
full industrial-EV lifecycle — **supply chain → assets & fleet → Net Zero**:

| Module | Stage | What it does | Ports |
| --- | --- | --- | --- |
| **[CellSentry](cellsentry/)** | ⛓ Upstream · supply chain | Graph-based battery-material supply-chain risk & traceability with a quantifiable detection lead time | API `:8001` |
| **[FleetMind](fleetmind/)** | 🔋 Midstream · assets & fleet | Battery SoH/RUL (NASA-validated), predictive maintenance, and fleet electrification readiness + EV procurement | API `:8002` |
| **[CarbonPulse](carbon_tracker/)** | 🌱 Outcome · Net Zero | Scope 1/3 carbon accounting vs SBTi targets, geospatial route analytics, AI electrification priorities | API `:8003` |
| **[Fleet Guardian](fleet_guardian/)** | 🔋 Midstream · APM agent | Cycle-level battery APM: RUL with confidence bands, temperature/voltage anomaly detection, LLM maintenance reasoning | API `:8004` |

All four render inside the **unified Urja UI at `:3000`** — one Next.js app,
one navigation, one design system. No module hops between separate sites.

## Run the whole platform

### Prerequisites
Make sure you have **Python 3** and **Node.js** (with `npm`) installed on your machine.

### Installation & Launch

One command brings up all four module APIs plus the unified UI:

```bash
# 1. Make the scripts executable (if not already)
chmod +x setup.sh run_platform.sh

# 2. Run the one-time setup (creates Python venvs + installs all backend/frontend dependencies)
./setup.sh

# 3. Launch all four module APIs + the unified UI (Ctrl-C stops all)
./run_platform.sh
```

*(Note: Each module uses LLMs for advanced reasoning and requires its own API key for full AI functionality. If omitted, they will either fall back to deterministic mocks or disable the AI features. You can `export` them before running the script:
- `export ANTHROPIC_API_KEY="your_anthropic_key"` (for CellSentry & FleetMind)
- `export GEMINI_API_KEY="your_gemini_key"` (for CarbonPulse)
- `export GROQ_API_KEY="your_groq_key"` (for Fleet Guardian))*

Then open the platform: **http://localhost:3000**

The launcher runs the four module APIs on `:8001`–`:8004` and the unified UI on
`:3000`, wiring CORS and API bases via environment variables. Module backends
are untouched (CarbonPulse's port was made configurable; its deps re-floored
for newer Python).

### Run a single module
Each module is self-contained and still runs on its own — see its own README
under `cellsentry/`, `fleetmind/`, `carbon_tracker/`, `fleet_guardian/`.

## Architecture

The integrated platform architecture — how the modules compose and share the
EV-lifecycle narrative — is in **[PLATFORM.md](PLATFORM.md)**. Each module has
its own detailed architecture under `*/docs/` or `*/SYSTEM_ARCHITECTURE.md`.

## Integrated story

- **CellSentry** protects the batteries you buy (upstream supply risk).
- **FleetMind** gets the most life out of the batteries you run and plans the
  switch to electric (asset performance + electrification).
- **Fleet Guardian** acts as the cycle-level APM agent, providing LLM-driven maintenance reasoning and real-time anomaly detection.
- **CarbonPulse** proves the resulting decarbonisation against Net-Zero targets.

Supply → Assets → Net Zero, end to end.

---

## Monorepo provenance

This repository merges four projects with full Git history preserved (merged
2026-07-11) from:
1. `https://github.com/De-Coder05/cellsentry`
2. `https://github.com/De-Coder05/fleetmind`
3. `https://github.com/janya1908/Carbon_tracker`
4. `https://github.com/mayankm2105/Fleet-Guardian-Agent-ET-AI-HACKATHON-2.0-`

## Troubleshooting

**The UI 404s on `main-app.js` / `layout.css` / `page.js`.**
Something ran `npm run build` (or `next build`) in `platform-new/` while the dev
server was running — both write to `platform-new/.next/`, so the production build
overwrites the dev chunk manifest and every dev chunk 404s. Fix:

```bash
# stop the dev server first, then:
rm -rf platform-new/.next
./run_platform.sh
```
