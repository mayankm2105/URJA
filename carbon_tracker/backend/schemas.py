from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FleetBase(BaseModel):
    name: str
    operator: str
    asset_class: str
    total_vehicles: int
    ev_vehicles: int
    diesel_vehicles: int
    avg_daily_km: float
    avg_payload_tons: float
    hub_city: str
    lat: float
    lon: float
    net_zero_target_year: int


class FleetOut(FleetBase):
    id: int
    ev_penetration_pct: float = 0.0
    readiness_index: float = 0.0
    model_config = {"from_attributes": True}


class RouteBase(BaseModel):
    name: str
    origin_city: str
    dest_city: str
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float
    distance_km: float
    trips_per_month: int
    vehicle_type: str
    payload_tons: float
    co2_per_km_kg: float
    ev_co2_per_km_kg: float
    is_electrified: bool


class RouteOut(RouteBase):
    id: int
    fleet_id: int
    monthly_co2_tons: float = 0.0
    potential_saving_tons: float = 0.0
    model_config = {"from_attributes": True}


class EmissionPoint(BaseModel):
    year: int
    month: int
    scope1_tons: float
    scope3_tons: float
    ev_avoided_tons: float
    target_tons: float
    label: str


class DashboardKPI(BaseModel):
    total_fleets: int
    total_vehicles: int
    ev_penetration_pct: float
    scope1_ytd_tons: float
    scope3_ytd_tons: float
    ev_avoided_ytd_tons: float
    net_zero_progress_pct: float
    routes_electrified: int
    total_routes: int
    top_priority_fleet: str
    carbon_saved_vs_target_pct: float


class PriorityItem(BaseModel):
    rank: int
    fleet_id: int
    fleet_name: str
    operator: str
    asset_class: str
    hub_city: str
    ev_penetration_pct: float
    annual_co2_tons: float
    potential_saving_tons: float
    readiness_index: float
    impact_score: float
    recommendation: str
    lat: float
    lon: float


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    reply: str
    intent: str
    data_refs: Optional[List[str]] = []


class CommitmentOut(BaseModel):
    id: int
    organization: str
    baseline_year: int
    target_year: int
    baseline_scope1_tons: float
    baseline_scope3_tons: float
    reduction_target_pct: float
    current_reduction_pct: float
    status: str
    model_config = {"from_attributes": True}


class SupplierOut(BaseModel):
    id: int
    name: str
    material: str
    country: str
    risk_score: float
    carbon_intensity: float
    concentration_pct: float
    model_config = {"from_attributes": True}
