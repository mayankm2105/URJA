"""Remaining-useful-life (RUL) projection.

Given a fitted degradation curve and an asset's current usage rate, project SoH
forward day by day until it crosses the end-of-life knee (default 80%). Because
the fitted loss is monotonically increasing in both EFC and days, the crossing
is unique and we locate it by bisection on elapsed days.
"""
from __future__ import annotations

from ..config import get_settings
from .estimator import DegradationFit

# How far ahead we are willing to extrapolate before calling an asset
# effectively "no foreseeable EoL" (10 years).
_MAX_HORIZON_DAYS = 3650


def health_band(soh: float) -> str:
    if soh >= 0.90:
        return "healthy"
    if soh >= get_settings().eol_soh:
        return "aging"
    return "end_of_life"


def predict_rul(
    fit: DegradationFit, efc_total: float, day_total: float, efc_per_day: float
) -> dict:
    """Project to the EoL threshold from the asset's current state.

    Returns RUL in days and in EFC, plus the projected end-of-life calendar
    offset. If the asset is already below threshold, RUL is 0.
    """
    eol = get_settings().eol_soh
    rate = max(efc_per_day, 1e-9)

    def soh_after(delta_days: float) -> float:
        return fit.soh_at(efc_total + rate * delta_days, day_total + delta_days)

    current = fit.soh_at(efc_total, day_total)
    if current <= eol:
        return {
            "rul_days": 0,
            "rul_efc": 0,
            "soh_now": round(current, 4),
            "eol_soh": eol,
            "horizon_capped": False,
        }

    # If we still haven't hit EoL at the max horizon, report it capped.
    if soh_after(_MAX_HORIZON_DAYS) > eol:
        return {
            "rul_days": _MAX_HORIZON_DAYS,
            "rul_efc": round(rate * _MAX_HORIZON_DAYS, 1),
            "soh_now": round(current, 4),
            "eol_soh": eol,
            "horizon_capped": True,
        }

    lo, hi = 0.0, float(_MAX_HORIZON_DAYS)
    for _ in range(60):
        mid = (lo + hi) / 2
        if soh_after(mid) > eol:
            lo = mid
        else:
            hi = mid
    rul_days = (lo + hi) / 2
    return {
        "rul_days": round(rul_days, 1),
        "rul_efc": round(rate * rul_days, 1),
        "soh_now": round(current, 4),
        "eol_soh": eol,
        "horizon_capped": False,
    }


def projection_series(
    fit: DegradationFit,
    efc_total: float,
    day_total: float,
    efc_per_day: float,
    rul_days: float,
    points: int = 24,
) -> list[dict]:
    """Forward SoH curve from today to (a bit past) projected EoL, for charting."""
    rate = max(efc_per_day, 1e-9)
    span = max(rul_days * 1.15, 30.0)
    out: list[dict] = []
    for i in range(points + 1):
        d = span * i / points
        out.append(
            {
                "day": round(day_total + d, 1),
                "efc": round(efc_total + rate * d, 1),
                "soh_predicted": round(fit.soh_at(efc_total + rate * d, day_total + d), 4),
            }
        )
    return out
