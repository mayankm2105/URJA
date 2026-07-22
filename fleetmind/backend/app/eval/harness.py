"""Evaluation harness — the headline degradation-prediction metrics for the deck.

PS3's fleet eval focus is "battery-degradation prediction accuracy vs observed
data". We measure it honestly with a temporal holdout:

  * Fit each asset's degradation curve on only the first `cutoff` fraction of
    its observed (noisy) history.
  * SoH accuracy  — predict SoH at every held-out future timestamp and compare
    to the ground-truth trajectory. Reported as MAE / RMSE in SoH percentage
    points across the whole fleet.
  * RUL accuracy  — from the cutoff, project time-to-80%-knee and compare to the
    true remaining life. Reported as median absolute error in days and MAPE.

All deterministic and runnable headless (no API key needed).
"""
from __future__ import annotations

import math

from ..config import get_settings
from ..data import fleet
from ..soh import degradation as deg
from ..soh import estimator, pooled, rul

_MAX_HORIZON_DAYS = 3650


def _true_eol_day(spec: dict) -> float | None:
    """Solve the ground-truth SoH curve for the day it crosses the EoL knee.
    Returns None if it does not within the 10-year horizon."""
    eol = get_settings().eol_soh
    rate = fleet.efc_per_day(spec)
    if deg.soh(spec, rate * _MAX_HORIZON_DAYS, _MAX_HORIZON_DAYS) > eol:
        return None
    lo, hi = 0.0, float(_MAX_HORIZON_DAYS)
    for _ in range(60):
        mid = (lo + hi) / 2
        if deg.soh(spec, rate * mid, mid) > eol:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def evaluate_soh(cutoff: float = 0.6) -> dict:
    """Hold out the late portion of each asset; score predicted vs true SoH."""
    abs_errs: list[float] = []
    sq_errs: list[float] = []
    held_points = 0
    for spec in fleet.ASSET_SPECS:
        series = fleet.observed_series(spec)
        k = max(2, int(len(series) * cutoff))
        train, test = series[:k], series[k:]
        if not test:
            continue
        fit = estimator.fit(train)
        for p in test:
            err = fit.soh_at(p["efc"], p["day"]) - p["soh_true"]
            abs_errs.append(abs(err))
            sq_errs.append(err * err)
            held_points += 1
    n = len(abs_errs)
    mae = sum(abs_errs) / n if n else 0.0
    rmse = math.sqrt(sum(sq_errs) / n) if n else 0.0
    return {
        "assets": len(fleet.ASSET_SPECS),
        "held_out_points": held_points,
        "cutoff_fraction": cutoff,
        "soh_mae_pct": round(mae * 100, 3),
        "soh_rmse_pct": round(rmse * 100, 3),
    }


def evaluate_rul(cutoff: float = 0.6) -> dict:
    """From the cutoff point, project time-to-EoL vs the ground-truth life."""
    abs_day_errs: list[float] = []
    ape: list[float] = []
    scored = 0
    for spec in fleet.ASSET_SPECS:
        true_eol = _true_eol_day(spec)
        if true_eol is None:
            continue  # no finite EoL within horizon -> RUL undefined to score
        series = fleet.observed_series(spec)
        k = max(2, int(len(series) * cutoff))
        train = series[:k]
        cut = train[-1]
        rul_true = true_eol - cut["day"]
        if rul_true <= 0:
            continue  # already past EoL at the cutoff
        fit = estimator.fit(train)
        rate = fleet.efc_per_day(spec)
        pred = rul.predict_rul(fit, cut["efc"], cut["day"], rate)
        rul_pred = pred["rul_days"]
        abs_day_errs.append(abs(rul_pred - rul_true))
        ape.append(abs(rul_pred - rul_true) / rul_true)
        scored += 1
    abs_day_errs.sort()
    ape.sort()
    median_days = abs_day_errs[len(abs_day_errs) // 2] if abs_day_errs else None
    median_ape = ape[len(ape) // 2] if ape else None
    return {
        "assets_scored": scored,
        "cutoff_fraction": cutoff,
        "rul_median_abs_err_days": round(median_days, 1) if median_days is not None else None,
        "rul_mean_abs_err_days": round(sum(abs_day_errs) / len(abs_day_errs), 1) if abs_day_errs else None,
        "rul_mape_pct": round(median_ape * 100, 1) if median_ape is not None else None,
    }


def evaluate_coefficient_recovery() -> dict:
    """Validate the fleet-pooled fit: do the recovered cycle/calendar
    coefficients match the ground-truth generating coefficients?"""
    model = pooled.get_pooled_model()
    per_chem: dict[str, dict] = {}
    rel_errs: list[float] = []
    for chem, fit in model.items():
        truth = deg.CHEMISTRY[chem]
        entry: dict[str, dict] = {}
        for key in ("b_cyc", "b_cal"):
            rel = abs(fit[key] - truth[key]) / truth[key]
            rel_errs.append(rel)
            entry[key] = {
                "fitted": round(fit[key], 6),
                "truth": round(truth[key], 6),
                "rel_err_pct": round(rel * 100, 2),
            }
        entry["n_assets"] = fit["n_assets"]
        entry["n_points"] = fit["n_points"]
        per_chem[chem] = entry
    return {
        "max_rel_err_pct": round(max(rel_errs) * 100, 2) if rel_errs else None,
        "mean_rel_err_pct": round(sum(rel_errs) / len(rel_errs) * 100, 2) if rel_errs else None,
        "per_chemistry": per_chem,
    }


def run_all() -> dict:
    return {
        "soh_prediction": evaluate_soh(),
        "rul_prediction": evaluate_rul(),
        "coefficient_recovery": evaluate_coefficient_recovery(),
    }
