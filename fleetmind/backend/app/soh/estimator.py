"""SoH estimator — fits the degradation prior to observed BMS data.

Capacity fade has two regimes the model must span:

    1 - SoH  =  a * sqrt(EFC)  +  c * EFC

The sqrt term is early-life, SEI-limited fade (Severson et al. 2019); the linear
term captures the accelerating late-life wear-out / "knee" that real cells show
(and that a pure-sqrt model badly under-predicts). The two bases are *not*
collinear, so both coefficients are identifiable from a single cell's history.
Constraining a, c >= 0 keeps the fit physical (capacity does not recover).

Within one constant-duty asset, EFC = rate * days, so cycle and calendar ageing
are not separable here (that is the fleet-pooled job in pooled.py); the EFC clock
absorbs both. The estimator only ever sees `soh_observed`, never the ground
truth — which is what makes the eval an honest accuracy measure.
"""
from __future__ import annotations

import math

import numpy as np


class DegradationFit:
    """Fitted per-asset degradation curve: loss = a*sqrt(EFC) + c*EFC."""

    def __init__(self, a: float, c: float, n: int, rmse: float) -> None:
        self.a = a          # sqrt (SEI / early-life) fade coefficient
        self.c = c          # linear (late-life wear-out) fade coefficient
        self.n = n          # number of points fitted
        self.rmse = rmse    # in-sample fit RMSE (SoH fraction)

    def soh_at(self, efc: float, days: float = 0.0) -> float:
        e = max(efc, 0.0)
        loss = self.a * math.sqrt(e) + self.c * e
        return max(0.0, min(1.0, 1.0 - loss))


def _refit_single(col: np.ndarray, loss: np.ndarray) -> float:
    denom = float(np.dot(col, col))
    return max(0.0, float(np.dot(col, loss) / denom)) if denom > 0 else 0.0


def fit(series: list[dict]) -> DegradationFit:
    """Fit (a, c) to a list of {efc, soh_observed} points by least squares."""
    efc = np.array([p["efc"] for p in series], dtype=float)
    loss = 1.0 - np.array([p["soh_observed"] for p in series], dtype=float)

    sqrt_efc = np.sqrt(np.maximum(efc, 0.0))
    X = np.column_stack([sqrt_efc, np.maximum(efc, 0.0)])
    coeffs, *_ = np.linalg.lstsq(X, loss, rcond=None)
    a, c = float(coeffs[0]), float(coeffs[1])

    # Enforce physical non-negativity; if one term goes negative, drop it and
    # refit on the other basis alone.
    if a < 0 or c < 0:
        if a < 0 <= c:
            a, c = 0.0, _refit_single(X[:, 1], loss)
        elif c < 0 <= a:
            a, c = _refit_single(X[:, 0], loss), 0.0
        else:
            a, c = 0.0, 0.0

    pred = a * sqrt_efc + c * np.maximum(efc, 0.0)
    rmse = float(np.sqrt(np.mean((pred - loss) ** 2))) if len(loss) else 0.0
    return DegradationFit(a=a, c=c, n=len(series), rmse=rmse)
