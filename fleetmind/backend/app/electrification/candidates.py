"""Candidate (ICE / CNG) fleet to be evaluated for electrification.

A realistic India intra-city logistics + transit fleet currently running on
diesel / CNG, with the operational data an electrification assessment needs:
route length, payload, duty cycle, and depot dwell time (the charging window).

Fields
------
vehicle_class   : maps to EV catalog classes
powertrain      : current fuel (diesel / cng / petrol)
daily_km        : average distance per operating day
payload_kg      : typical payload carried (0 for pure passenger)
trips_per_day   : duty-cycle intensity
returns_to_depot: parks at a depot each night (enables overnight charging)
route_fixed     : fixed/scheduled route (vs on-demand/variable)
dwell_hours     : longest daily idle window available for charging
annual_km       : annual distance (for TCO)
fuel_cost_per_km: current running fuel cost (INR/km)
"""
from __future__ import annotations

CANDIDATES: list[dict] = [
    {
        "id": "del-3w-blr", "name": "Last-mile Cargo 3W · BLR-07", "region": "Bengaluru",
        "vehicle_class": "cargo_3w", "powertrain": "diesel", "daily_km": 75,
        "payload_kg": 350, "trips_per_day": 9, "returns_to_depot": True,
        "route_fixed": True, "dwell_hours": 11, "annual_km": 24000,
        "fuel_cost_per_km": 3.4,
    },
    {
        "id": "del-3w-ahm", "name": "Last-mile Cargo 3W · AHM-04", "region": "Ahmedabad",
        "vehicle_class": "cargo_3w", "powertrain": "diesel", "daily_km": 60,
        "payload_kg": 300, "trips_per_day": 8, "returns_to_depot": True,
        "route_fixed": True, "dwell_hours": 12, "annual_km": 19000,
        "fuel_cost_per_km": 3.2,
    },
    {
        "id": "del-3w-del", "name": "Last-mile Cargo 3W · DEL-11", "region": "Delhi",
        "vehicle_class": "cargo_3w", "powertrain": "cng", "daily_km": 95,
        "payload_kg": 480, "trips_per_day": 11, "returns_to_depot": True,
        "route_fixed": True, "dwell_hours": 8, "annual_km": 30000,
        "fuel_cost_per_km": 2.9,
    },
    {
        "id": "lcv-pun", "name": "City Logistics Van · PUN-02", "region": "Pune",
        "vehicle_class": "lcv", "powertrain": "diesel", "daily_km": 90,
        "payload_kg": 650, "trips_per_day": 5, "returns_to_depot": True,
        "route_fixed": True, "dwell_hours": 10, "annual_km": 28000,
        "fuel_cost_per_km": 7.1,
    },
    {
        "id": "lcv-mum", "name": "City Logistics Van · MUM-03", "region": "Mumbai",
        "vehicle_class": "lcv", "powertrain": "diesel", "daily_km": 135,
        "payload_kg": 850, "trips_per_day": 6, "returns_to_depot": True,
        "route_fixed": False, "dwell_hours": 8, "annual_km": 42000,
        "fuel_cost_per_km": 7.4,
    },
    {
        "id": "taxi-kol", "name": "Fleet Taxi Sedan · KOL-09", "region": "Kolkata",
        "vehicle_class": "sedan_taxi", "powertrain": "diesel", "daily_km": 175,
        "payload_kg": 0, "trips_per_day": 14, "returns_to_depot": True,
        "route_fixed": False, "dwell_hours": 6, "annual_km": 60000,
        "fuel_cost_per_km": 6.8,
    },
    {
        "id": "auto-jai", "name": "Passenger Auto · JAI-05", "region": "Jaipur",
        "vehicle_class": "passenger_3w", "powertrain": "cng", "daily_km": 110,
        "payload_kg": 0, "trips_per_day": 22, "returns_to_depot": True,
        "route_fixed": False, "dwell_hours": 9, "annual_km": 36000,
        "fuel_cost_per_km": 2.6,
    },
    {
        "id": "bus-hyd", "name": "City Bus · HYD-08", "region": "Hyderabad",
        "vehicle_class": "city_bus", "powertrain": "diesel", "daily_km": 190,
        "payload_kg": 0, "trips_per_day": 8, "returns_to_depot": True,
        "route_fixed": True, "dwell_hours": 7, "annual_km": 62000,
        "fuel_cost_per_km": 24.0,
    },
    {
        "id": "bus-blr", "name": "City Bus · BLR-01", "region": "Bengaluru",
        "vehicle_class": "city_bus", "powertrain": "diesel", "daily_km": 245,
        "payload_kg": 0, "trips_per_day": 9, "returns_to_depot": True,
        "route_fixed": True, "dwell_hours": 6, "annual_km": 80000,
        "fuel_cost_per_km": 25.5,
    },
    {
        "id": "truck-che", "name": "Intercity Truck · CHE-07", "region": "Chennai",
        "vehicle_class": "mcv_truck", "powertrain": "diesel", "daily_km": 380,
        "payload_kg": 3500, "trips_per_day": 2, "returns_to_depot": False,
        "route_fixed": False, "dwell_hours": 4, "annual_km": 120000,
        "fuel_cost_per_km": 14.0,
    },
]

_BY_ID = {c["id"]: c for c in CANDIDATES}


def get_candidate(candidate_id: str) -> dict | None:
    return _BY_ID.get(candidate_id)
