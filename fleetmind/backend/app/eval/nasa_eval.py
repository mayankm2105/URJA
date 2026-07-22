"""Real-data validation — NASA battery aging dataset.

Validates the *same* estimator and RUL projection that drive the operational
fleet against the four real NASA cells (B0005/6/7/18), two ways:

1. Model adequacy — fit the 2-mechanism curve (sqrt + linear) to each cell's
   full real trajectory and report the in-sample RMSE. This asks: does the model
   FORM actually represent real Li-ion degradation? (It does, to ~2% SoH.)

2. Knee-onset forecast — fit only each cell's early life, down to `fit_floor`
   SoH (the knee onset, default 85%), then forecast forward:
     * SoH MAE on the held-out later cycles vs the real measurements;
     * RUL: cycles-to-80%-knee projected from the cutoff vs the cell's real
       end-of-life cycle.
   This mirrors the operational task: once a pack shows knee onset, how well do
   we predict its 80% replacement point?

Honest by construction — forecasting an unobserved knee is hard, and the error
shrinks as more of the trajectory is seen.
"""
from __future__ import annotations

import math

from ..data import nasa
from ..soh import estimator, rul


def model_adequacy() -> dict:
    """Full-trajectory in-sample fit RMSE per cell — does the form fit reality?"""
    per_cell = []
    for cid in nasa.cell_ids():
        f = estimator.fit(nasa.observed_series(cid))
        per_cell.append(
            {
                "cell": cid,
                "a_sqrt": round(f.a, 6),
                "c_linear": round(f.c, 6),
                "in_sample_rmse_pct": round(f.rmse * 100, 3),
            }
        )
    rmses = [c["in_sample_rmse_pct"] for c in per_cell]
    return {
        "mean_rmse_pct": round(sum(rmses) / len(rmses), 3),
        "max_rmse_pct": round(max(rmses), 3),
        "per_cell": per_cell,
    }


def _forecast_cell(cell_id: str, fit_floor: float) -> dict | None:
    series = nasa.observed_series(cell_id)
    true_eol = nasa.true_eol_cycle(cell_id)
    k = 0
    while k < len(series) and series[k]["soh_observed"] >= fit_floor:
        k += 1
    k = max(3, k)
    train, test = series[:k], series[k:]
    if not test:
        return None
    fit = estimator.fit(train)
    cut = train[-1]

    abs_errs = [abs(fit.soh_at(p["efc"]) - p["soh_true"]) for p in test]
    soh_mae = sum(abs_errs) / len(abs_errs)

    rul_row = None
    if true_eol is not None:
        rul_true = true_eol - cut["efc"]
        if rul_true > 0:
            pred = rul.predict_rul(fit, cut["efc"], cut["efc"], 1.0)  # efc/day=1 -> cycles
            rul_row = {
                "fit_window_cycles": len(train),
                "cutoff_soh_pct": round(cut["soh_observed"] * 100, 1),
                "true_eol_cycle": round(true_eol),
                "rul_true_cycles": round(rul_true),
                "rul_pred_cycles": round(pred["rul_days"]),
                "rul_abs_err_cycles": round(abs(pred["rul_days"] - rul_true), 1),
            }
    return {
        "cell": cell_id,
        "held_out_cycles": len(test),
        "soh_mae_pct": round(soh_mae * 100, 3),
        "rul": rul_row,
    }


def forecast(fit_floor: float = 0.85) -> dict:
    per_cell = [r for cid in nasa.cell_ids() if (r := _forecast_cell(cid, fit_floor))]
    maes = [r["soh_mae_pct"] for r in per_cell]
    rul_errs = sorted(r["rul"]["rul_abs_err_cycles"] for r in per_cell if r["rul"])
    return {
        "fit_window": f"early life to {fit_floor * 100:.0f}% SoH (knee onset)",
        "soh_mae_pct_mean": round(sum(maes) / len(maes), 3) if maes else None,
        "soh_mae_pct_max": round(max(maes), 3) if maes else None,
        "rul_median_abs_err_cycles": rul_errs[len(rul_errs) // 2] if rul_errs else None,
        "rul_mean_abs_err_cycles": round(sum(rul_errs) / len(rul_errs), 1) if rul_errs else None,
        "per_cell": per_cell,
    }


def evaluate() -> dict:
    return {
        "source": "NASA Li-ion Battery Aging Dataset (B0005/B0006/B0007/B0018, 2Ah 18650, 24C)",
        "cells": len(nasa.cell_ids()),
        "model_adequacy": model_adequacy(),
        "knee_onset_forecast": forecast(),
    }
