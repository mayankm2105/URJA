"""Fleet-pooled degradation fit — separating cycle vs calendar ageing.

A single constant-duty asset cannot distinguish cycle from calendar ageing:
EFC = rate · days, so √EFC and √days are collinear and only their *combined*
fade rate is identifiable (see estimator.py).

Pooling the fleet breaks the degeneracy. For all observations of a given
chemistry we regress

    1 - SoH_ij  =  b_cyc · cycle_stress_i · √EFC_ij
                 + b_cal · calendar_stress_i · √days_ij

where the per-asset stress factors are computed from *observed telematics*
(average cell temperature, depth-of-discharge, C-rate). Because assets differ
in duty cycle and operating conditions, the two design columns are no longer
proportional across the pooled dataset, so the physical base coefficients
b_cyc and b_cal become identifiable.

This both (a) recovers interpretable physics from data and (b) lets us split any
asset's capacity loss into a data-derived cycle vs calendar contribution — which
eval/harness.py validates against the ground-truth generating coefficients.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from ..data import fleet
from . import degradation as deg


def _fit_chemistry(specs: list[dict]) -> dict:
    rows_cyc: list[float] = []
    rows_cal: list[float] = []
    target: list[float] = []
    for spec in specs:
        cs = deg.cycle_stress(spec["cell_temp_c"], spec["avg_dod"], spec["avg_c_rate"])
        ks = deg.calendar_stress(spec["cell_temp_c"])
        for p in fleet.observed_series(spec):
            rows_cyc.append(cs * (max(p["efc"], 0.0) ** 0.5))
            rows_cal.append(ks * (max(p["day"], 0.0) ** 0.5))
            target.append(1.0 - p["soh_observed"])

    X = np.column_stack([rows_cyc, rows_cal])
    y = np.array(target, dtype=float)
    coeffs, *_ = np.linalg.lstsq(X, y, rcond=None)
    b_cyc, b_cal = float(coeffs[0]), float(coeffs[1])

    # Enforce physical non-negativity; if one term is driven negative by
    # residual collinearity, drop it and refit on the other column alone.
    if b_cyc < 0 or b_cal < 0:
        if b_cyc < 0 <= b_cal:
            col = X[:, 1:2]
            sol, *_ = np.linalg.lstsq(col, y, rcond=None)
            b_cyc, b_cal = 0.0, max(0.0, float(sol[0]))
        elif b_cal < 0 <= b_cyc:
            col = X[:, 0:1]
            sol, *_ = np.linalg.lstsq(col, y, rcond=None)
            b_cyc, b_cal = max(0.0, float(sol[0])), 0.0
        else:
            b_cyc, b_cal = max(0.0, b_cyc), max(0.0, b_cal)

    pred = b_cyc * X[:, 0] + b_cal * X[:, 1]
    rmse = float(np.sqrt(np.mean((pred - y) ** 2))) if len(y) else 0.0
    return {
        "b_cyc": b_cyc,
        "b_cal": b_cal,
        "n_points": len(y),
        "n_assets": len(specs),
        "rmse": rmse,
    }


@lru_cache(maxsize=1)
def get_pooled_model() -> dict:
    """Per-chemistry pooled coefficients, fit once over the whole fleet."""
    by_chem: dict[str, list[dict]] = {}
    for spec in fleet.ASSET_SPECS:
        by_chem.setdefault(spec["chemistry"], []).append(spec)
    return {chem: _fit_chemistry(specs) for chem, specs in by_chem.items()}


def fitted_attribution(spec: dict, efc: float, days: float) -> dict:
    """Split an asset's capacity loss into data-derived cycle vs calendar parts
    using the pooled coefficients (falls back to a degenerate split if the
    chemistry was not poolable)."""
    model = get_pooled_model().get(spec["chemistry"])
    if not model:
        return {"cycle_loss": 0.0, "calendar_loss": 0.0, "cycle_share": None}
    cs = deg.cycle_stress(spec["cell_temp_c"], spec["avg_dod"], spec["avg_c_rate"])
    ks = deg.calendar_stress(spec["cell_temp_c"])
    cyc = model["b_cyc"] * cs * (max(efc, 0.0) ** 0.5)
    cal = model["b_cal"] * ks * (max(days, 0.0) ** 0.5)
    total = cyc + cal
    return {
        "cycle_loss": cyc,
        "calendar_loss": cal,
        "cycle_share": (cyc / total) if total > 0 else None,
    }
