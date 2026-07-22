from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class AssetBase(BaseModel):
    battery_id: str
    display_name: str
    current_soh: float
    risk_tier: str
    last_updated_cycle: int

    model_config = ConfigDict(from_attributes=True)

class HealthResponse(BaseModel):
    battery_id: str
    current_soh: float
    current_cycle: int
    rul_cycles: float
    confidence_band_cycles: float
    confidence_level: str
    risk_tier: str
    slope_blend: float
    temperature_anomaly: bool
    voltage_sag_anomaly: bool

class RecommendationResponse(HealthResponse):
    explanation: str
    likely_cause: str
    recommendation: str
    urgency: str

class BatteryCycleResponse(BaseModel):
    cycle: int
    soh: float
    capacity: float
    temperature: float
    voltage: float

    model_config = ConfigDict(from_attributes=True)

class FleetSummaryResponse(BaseModel):
    total_assets: int
    healthy_count: int
    watch_count: int
    critical_count: int
    average_soh: float

class ErrorResponse(BaseModel):
    error: str
    detail: str
