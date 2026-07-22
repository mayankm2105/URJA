#!/usr/bin/env bash
# Launch the unified Urja platform.
#
#   Urja UI (all modules)   http://localhost:3000
#   CellSentry API             :8001
#   FleetMind API              :8002
#   CarbonPulse API            :8003   (also serves its original standalone UI)
#   Fleet Guardian API         :8004
#
# Run ./setup.sh once first. Ctrl-C stops everything.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PIDS=()
UI_ORIGIN="http://localhost:3000"

cleanup() {
  printf "\n\033[1;33mStopping platform...\033[0m\n"
  for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null || true; done
  wait 2>/dev/null || true
}
trap cleanup INT TERM EXIT

up() { printf "  \033[1;32m▶\033[0m %s\n" "$1"; }

printf "\033[1mStarting Urja platform...\033[0m\n"

up "CellSentry API      :8001"
( cd "$ROOT/cellsentry/backend" && CORS_ORIGINS="$UI_ORIGIN" \
    ./.venv/bin/uvicorn app.main:app --port 8001 ) & PIDS+=($!)

up "FleetMind API       :8002"
( cd "$ROOT/fleetmind/backend" && CORS_ORIGINS="$UI_ORIGIN" \
    ./.venv/bin/uvicorn app.main:app --port 8002 ) & PIDS+=($!)

up "CarbonPulse API     :8003"
( cd "$ROOT/carbon_tracker/backend" && PORT=8003 ALLOWED_ORIGINS="$UI_ORIGIN" \
    ../venv/bin/python main.py ) & PIDS+=($!)

up "Fleet Guardian API  :8004"
( cd "$ROOT/fleet_guardian/Fleet-Guardian-Backend" && \
    DATABASE_URL="sqlite+aiosqlite:///./test.db" GROQ_API_KEY="${GROQ_API_KEY:-dummy}" \
    ./venv/bin/uvicorn app.main:app --port 8004 ) & PIDS+=($!)

up "Urja UI          :3000"
( cd "$ROOT/platform-new" && npm run dev ) & PIDS+=($!)

printf "\n  \033[1;36mUrja platform up →  http://localhost:3000\033[0m\n"
printf "  (UI takes ~10-20s on first compile)\n"
printf "  Ctrl-C to stop everything.\n\n"
wait
