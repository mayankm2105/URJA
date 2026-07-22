"""Pydantic models for the API."""
from typing import Optional

from pydantic import BaseModel, Field


class Node(BaseModel):
    id: str
    label: str
    type: str  # product | pack | cell | material | raw_material | supplier | country
    tier: Optional[int] = None
    country: Optional[str] = None
    country_shares: Optional[dict[str, float]] = None
    risk: float = 0.0
    risk_band: str = "low"  # low | medium | high
    baseline_risk: Optional[float] = None  # risk with no active events (for delta)
    lead_time_days: Optional[float] = None  # products only: days until an active shock bites
    risk_breakdown: dict[str, float] = Field(default_factory=dict)


class Edge(BaseModel):
    source: str
    target: str
    type: str = "supplies"
    dependency: float = 1.0
    buffer_days: float = 0.0


class GraphResponse(BaseModel):
    nodes: list[Node]
    edges: list[Edge]
    meta: dict = Field(default_factory=dict)


class EventSource(BaseModel):
    name: str
    url: Optional[str] = None


class Event(BaseModel):
    id: str
    date: str
    headline: str
    body: Optional[str] = None
    source: EventSource
    event_type: str
    severity: int
    direction: str
    materials: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    suppliers: list[str] = Field(default_factory=list)


class Alert(BaseModel):
    product_id: str
    product_label: str
    scenario_risk: float
    baseline_risk: float
    delta: float
    risk_band: str
    lead_time_days: Optional[float] = None
    path_labels: list[str] = Field(default_factory=list)  # shock -> ... -> product
    via_label: Optional[str] = None  # the shocked upstream node driving the lead time
    triggering_event_ids: list[str] = Field(default_factory=list)
    triggering_headlines: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    brief: str = ""


class ScenarioRequest(BaseModel):
    event_ids: list[str] = Field(default_factory=list)
    generate_briefs: bool = True


class ScenarioResponse(BaseModel):
    nodes: list[Node]
    edges: list[Edge]
    alerts: list[Alert]
    events_applied: list[str] = Field(default_factory=list)
    meta: dict = Field(default_factory=dict)
