"""Pydantic models for the API."""
from typing import Optional

from pydantic import BaseModel, Field


class AssetSummary(BaseModel):
    id: str
    name: str
    vehicle_type: str
    region: str
    chemistry: str
    soh: float                      # current State-of-Health, 0-1
    soh_band: str                   # healthy | aging | end_of_life
    rul_days: float                 # projected days to 80% knee
    rul_efc: float                  # projected equivalent full cycles to knee
    efc_total: float                # cumulative EFC today
    age_days: int
    dominant_driver: str
    horizon_capped: bool = False    # True when EoL is beyond the 10y horizon


class SohPoint(BaseModel):
    day: float
    efc: float
    soh_observed: Optional[float] = None
    soh_true: Optional[float] = None
    soh_predicted: Optional[float] = None


class AssetDetail(BaseModel):
    summary: AssetSummary
    fit: dict                       # {a, b, n, rmse}
    fade_breakdown: dict            # {cycle_loss, calendar_loss}
    history: list[SohPoint]         # observed series (with ground truth)
    projection: list[SohPoint]      # forward prediction to EoL
    recommendations: list[str] = Field(default_factory=list)
    brief: str = ""


class FleetResponse(BaseModel):
    assets: list[AssetSummary]
    meta: dict = Field(default_factory=dict)
