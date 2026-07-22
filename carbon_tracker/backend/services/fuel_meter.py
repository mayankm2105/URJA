"""Metered fuel logs — the ground truth carbon accounting is validated against.

PS3 evaluates "demonstrated carbon tracking accuracy **against actual emission
measurements**". A depot does not measure CO2 directly; it measures **litres
dispensed**. Emissions are then litres x a published factor (2.68 kg CO2e/L),
which is a constant, not a modelling choice.

So the thing that can actually be *wrong* — and therefore the thing worth
validating — is the engine's **fuel-consumption assumption**: `carbon_engine`
estimates km/litre from a payload tier (10 / 6 / 4 / 2 km/L). Reality varies
around that for reasons the engine cannot see.

This module simulates the depot's fuel meter. Consumption is generated from a
*richer* process than the estimator uses:

  * terrain/gradient on the corridor (ghats burn far more than plains),
  * urban congestion (idling destroys economy on short city legs),
  * driver behaviour spread across a real driver roster,
  * load-factor variance (trucks rarely run at nameplate payload),
  * a small meter/reconciliation error.

None of those are inputs to `diesel_co2_per_km()`, so the resulting error is a
genuine measure of the estimator's blind spots rather than a restatement of its
own arithmetic.

HONEST LIMITATION: these are *simulated* meter readings calibrated to published
Indian fleet fuel-economy ranges, not a real telematics feed. Unlike the NASA
battery validation — which uses genuinely real cells — this validates the
estimator against a realistic model of reality, not reality itself. Swap in a
real fuel-card/telematics export and this module is the only thing that changes.
"""
from __future__ import annotations

import random
import zlib

DIESEL_CO2_PER_LITRE = 2.68  # kg CO2e — published constant, not fitted

# Corridor character, keyed by the route's city pair. Real Indian freight
# corridors differ enormously: the Mumbai-Pune ghat section vs the flat
# Delhi-Jaipur run is a ~25% economy swing.
TERRAIN = {
    ("Mumbai", "Pune"): 1.18,        # Bhor ghat climb
    ("Chennai", "Bengaluru"): 1.05,
    ("Delhi", "Jaipur"): 0.96,       # flat NH48
    ("Kolkata", "Ranchi"): 1.12,     # Chota Nagpur plateau
    ("Ahmedabad", "Mumbai"): 0.98,
    ("Hyderabad", "Vijayawada"): 0.99,
}

# Short city legs idle far more; long-haul cruises efficiently.
def _congestion_penalty(distance_km: float) -> float:
    if distance_km <= 60:
        return 1.22   # dense urban duty
    if distance_km <= 150:
        return 1.08
    if distance_km <= 350:
        return 1.01
    return 0.97       # highway cruise


def _terrain(origin: str, dest: str) -> float:
    return TERRAIN.get((origin, dest), TERRAIN.get((dest, origin), 1.03))


def meter_route(route: dict) -> dict:
    """One month of metered diesel for a route, plus the CO2 it implies.

    Deterministic per route id so the accuracy numbers are reproducible.
    """
    rng = random.Random(zlib.crc32(f"meter-{route['id']}".encode()))

    payload = float(route.get("payload_tons") or 0.0)
    distance = float(route["distance_km"])
    trips = int(route.get("trips_per_month") or 0)

    # Baseline economy the *world* actually delivers for this payload class.
    if payload <= 2.0:
        base_kmpl = 9.4
    elif payload <= 10.0:
        base_kmpl = 5.7
    elif payload <= 20.0:
        base_kmpl = 3.9
    else:
        base_kmpl = 2.1

    # Hidden factors the estimator has no visibility of.
    terrain = _terrain(route["origin_city"], route["dest_city"])
    congestion = _congestion_penalty(distance)
    driver = rng.uniform(0.94, 1.09)          # roster spread
    load_factor = rng.uniform(0.97, 1.06)     # rarely at nameplate payload
    meter_err = rng.uniform(0.995, 1.005)     # reconciliation noise

    effective_kmpl = base_kmpl / (terrain * congestion * driver * load_factor)
    km = distance * trips
    litres = (km / effective_kmpl) * meter_err if effective_kmpl > 0 else 0.0

    return {
        "route_id": route["id"],
        "route": route["name"],
        "km_run": round(km, 1),
        "litres_metered": round(litres, 1),
        "effective_kmpl": round(effective_kmpl, 2),
        "measured_tco2": round(litres * DIESEL_CO2_PER_LITRE / 1000.0, 3),
    }


def meter_fleet(routes: list[dict]) -> list[dict]:
    """Meter every diesel route (electrified routes burn no diesel)."""
    return [
        meter_route(r)
        for r in routes
        if not r.get("is_electrified") and (r.get("trips_per_month") or 0) > 0
    ]
