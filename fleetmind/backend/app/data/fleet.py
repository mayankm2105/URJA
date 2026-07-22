"""Synthetic-but-physical EV fleet.

Each asset has a static spec (chemistry, duty cycle, climate). From that spec
the degradation model produces a ground-truth SoH trajectory; we then sample it
on a weekly telemetry cadence and add realistic BMS capacity-estimate noise to
get the *observed* series the estimator is allowed to see.

The fleet is deliberately diverse — a hot-climate heavy NMC bus that is almost
spent, a gently-driven LFP rickshaw that is barely aged, fast-charged delivery
vans, etc. — so the health board shows a clear spread and the predictive-
maintenance story has an obvious headline asset.

Spec fields
-----------
chemistry            : "NMC" | "LFP"
nominal_kwh          : usable nameplate energy
km_per_day           : average daily distance
kwh_per_km           : energy consumption (vehicle mass / duty dependent)
cell_temp_c          : average cell temperature (climate + thermal load)
avg_dod              : average depth of discharge per cycle
avg_c_rate           : average charge/discharge C-rate (fast charging => high)
in_service_days      : age of the asset today
"""
from __future__ import annotations

import random
import zlib

from ..soh import degradation as deg

# BMS capacity-estimate noise (1 sigma), as a fraction of SoH. Real packs
# report coulomb-counting / OCV capacity to within ~0.6%.
BMS_NOISE_SIGMA = 0.006

# Telemetry cadence: one capacity datapoint per week.
SAMPLE_EVERY_DAYS = 7


ASSET_SPECS: list[dict] = [
    {
        "id": "bus-blr-01", "name": "City Bus 01", "vehicle_type": "e-bus",
        "region": "Bengaluru", "chemistry": "NMC", "nominal_kwh": 250.0,
        "km_per_day": 210.0, "kwh_per_km": 1.05, "cell_temp_c": 41.0,
        "avg_dod": 0.88, "avg_c_rate": 1.10, "in_service_days": 1320,
    },
    {
        "id": "bus-del-02", "name": "City Bus 02", "vehicle_type": "e-bus",
        "region": "Delhi", "chemistry": "NMC", "nominal_kwh": 250.0,
        "km_per_day": 190.0, "kwh_per_km": 1.02, "cell_temp_c": 38.0,
        "avg_dod": 0.80, "avg_c_rate": 0.85, "in_service_days": 980,
    },
    {
        "id": "van-mum-03", "name": "Delivery Van 03", "vehicle_type": "e-van",
        "region": "Mumbai", "chemistry": "NMC", "nominal_kwh": 60.0,
        "km_per_day": 140.0, "kwh_per_km": 0.22, "cell_temp_c": 36.0,
        "avg_dod": 0.75, "avg_c_rate": 1.40, "in_service_days": 760,
    },
    {
        "id": "van-pun-04", "name": "Delivery Van 04", "vehicle_type": "e-van",
        "region": "Pune", "chemistry": "LFP", "nominal_kwh": 60.0,
        "km_per_day": 120.0, "kwh_per_km": 0.21, "cell_temp_c": 30.0,
        "avg_dod": 0.70, "avg_c_rate": 0.70, "in_service_days": 900,
    },
    {
        "id": "rck-jai-05", "name": "E-Rickshaw 05", "vehicle_type": "e-rickshaw",
        "region": "Jaipur", "chemistry": "LFP", "nominal_kwh": 8.0,
        "km_per_day": 90.0, "kwh_per_km": 0.055, "cell_temp_c": 33.0,
        "avg_dod": 0.65, "avg_c_rate": 0.50, "in_service_days": 1100,
    },
    {
        "id": "rck-luc-06", "name": "E-Rickshaw 06", "vehicle_type": "e-rickshaw",
        "region": "Lucknow", "chemistry": "LFP", "nominal_kwh": 8.0,
        "km_per_day": 70.0, "kwh_per_km": 0.052, "cell_temp_c": 28.0,
        "avg_dod": 0.55, "avg_c_rate": 0.45, "in_service_days": 540,
    },
    {
        "id": "van-che-07", "name": "Delivery Van 07", "vehicle_type": "e-van",
        "region": "Chennai", "chemistry": "NMC", "nominal_kwh": 60.0,
        "km_per_day": 160.0, "kwh_per_km": 0.23, "cell_temp_c": 39.0,
        "avg_dod": 0.82, "avg_c_rate": 1.25, "in_service_days": 610,
    },
    {
        "id": "bus-hyd-08", "name": "City Bus 08", "vehicle_type": "e-bus",
        "region": "Hyderabad", "chemistry": "LFP", "nominal_kwh": 320.0,
        "km_per_day": 200.0, "kwh_per_km": 1.08, "cell_temp_c": 34.0,
        "avg_dod": 0.78, "avg_c_rate": 0.80, "in_service_days": 820,
    },
    {
        "id": "van-kol-09", "name": "Delivery Van 09", "vehicle_type": "e-van",
        "region": "Kolkata", "chemistry": "NMC", "nominal_kwh": 60.0,
        "km_per_day": 100.0, "kwh_per_km": 0.20, "cell_temp_c": 35.0,
        "avg_dod": 0.68, "avg_c_rate": 0.65, "in_service_days": 300,
    },
    {
        "id": "rck-ahm-10", "name": "E-Rickshaw 10", "vehicle_type": "e-rickshaw",
        "region": "Ahmedabad", "chemistry": "LFP", "nominal_kwh": 8.0,
        "km_per_day": 110.0, "kwh_per_km": 0.058, "cell_temp_c": 37.0,
        "avg_dod": 0.80, "avg_c_rate": 0.60, "in_service_days": 1240,
    },
]

_BY_ID = {s["id"]: s for s in ASSET_SPECS}


def efc_per_day(spec: dict) -> float:
    """Equivalent full cycles accrued per day from the duty cycle."""
    daily_kwh = spec["km_per_day"] * spec["kwh_per_km"]
    return daily_kwh / spec["nominal_kwh"]


def get_spec(asset_id: str) -> dict | None:
    return _BY_ID.get(asset_id)


def observed_series(spec: dict) -> list[dict]:
    """Weekly (day, efc, soh_observed, soh_true) samples from in-service to today.

    Deterministic: noise is seeded from a stable CRC32 of the asset id (NOT the
    process-randomised builtin hash) so the fleet — and therefore every eval
    number — is byte-identical across runs and machines.
    """
    rng = random.Random(zlib.crc32(spec["id"].encode()))
    rate = efc_per_day(spec)
    series: list[dict] = []
    day = 0
    while day <= spec["in_service_days"]:
        efc = rate * day
        true = deg.soh(spec, efc, day)
        noise = rng.gauss(0.0, BMS_NOISE_SIGMA)
        series.append(
            {
                "day": day,
                "efc": round(efc, 2),
                "soh_true": round(true, 5),
                "soh_observed": round(min(1.0, max(0.0, true + noise)), 5),
            }
        )
        day += SAMPLE_EVERY_DAYS
    return series


def current_state(spec: dict) -> dict:
    """Latest observed point plus cumulative totals at 'today'."""
    rate = efc_per_day(spec)
    days = spec["in_service_days"]
    efc = rate * days
    series = observed_series(spec)
    last = series[-1]
    return {
        "day": days,
        "efc_total": round(efc, 1),
        "efc_per_day": round(rate, 4),
        "soh_observed": last["soh_observed"],
        "soh_true": last["soh_true"],
    }
