#!/usr/bin/env bash
# One-time dependency setup for the Urja platform (all three modules).
# Creates Python venvs and installs backend + frontend dependencies.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

py() { python3 "$@"; }
step() { printf "\n\033[1;34m==>\033[0m %s\n" "$1"; }

step "CellSentry backend venv"
cd "$ROOT/cellsentry/backend" && py -m venv .venv && ./.venv/bin/pip install -q --upgrade pip && ./.venv/bin/pip install -q -r requirements.txt

step "FleetMind backend venv"
cd "$ROOT/fleetmind/backend" && py -m venv .venv && ./.venv/bin/pip install -q --upgrade pip && ./.venv/bin/pip install -q -r requirements.txt

step "CarbonPulse backend venv"
cd "$ROOT/carbon_tracker" && py -m venv venv && ./venv/bin/pip install -q --upgrade pip && ./venv/bin/pip install -q -r backend/requirements.txt

step "Fleet Guardian backend venv"
cd "$ROOT/fleet_guardian/Fleet-Guardian-Backend" && py -m venv venv && ./venv/bin/pip install -q --upgrade pip && ./venv/bin/pip install -q -r requirements.txt

step "Urja UI deps"
cd "$ROOT/platform-new" && npm install --silent

printf "\n\033[1;32m✓ Setup complete.\033[0m  Run ./run_platform.sh\n"
