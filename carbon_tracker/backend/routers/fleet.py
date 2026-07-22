from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db, Fleet
from schemas import FleetOut
from services.carbon_engine import electrification_readiness_index, diesel_co2_per_km, ev_co2_per_km

router = APIRouter()


@router.get("/fleet", response_model=List[FleetOut])
def get_fleet(db: Session = Depends(get_db)):
    fleets = db.query(Fleet).all()
    result = []
    for f in fleets:
        ev_pct = (f.ev_vehicles / max(f.total_vehicles, 1)) * 100
        ri = electrification_readiness_index(ev_pct, f.avg_daily_km, f.avg_payload_tons, f.asset_class)
        out = FleetOut(
            id=f.id, name=f.name, operator=f.operator, asset_class=f.asset_class,
            total_vehicles=f.total_vehicles, ev_vehicles=f.ev_vehicles,
            diesel_vehicles=f.diesel_vehicles, avg_daily_km=f.avg_daily_km,
            avg_payload_tons=f.avg_payload_tons, hub_city=f.hub_city,
            lat=f.lat, lon=f.lon, net_zero_target_year=f.net_zero_target_year,
            ev_penetration_pct=round(ev_pct, 1), readiness_index=ri,
        )
        result.append(out)
    return result


@router.get("/fleet/{fleet_id}/carbon")
def get_fleet_carbon(fleet_id: int, db: Session = Depends(get_db)):
    """Carbon profile for a specific fleet."""
    f = db.query(Fleet).filter(Fleet.id == fleet_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Fleet not found")
    d_co2 = diesel_co2_per_km(f.avg_payload_tons)
    e_co2 = ev_co2_per_km(f.avg_payload_tons)
    daily_km_total = f.avg_daily_km * f.diesel_vehicles
    annual_scope1 = (daily_km_total * 365 * d_co2) / 1000
    annual_ev_co2 = (f.avg_daily_km * f.ev_vehicles * 365 * e_co2) / 1000
    annual_avoided = (daily_km_total * 365 * (d_co2 - e_co2)) / 1000

    return {
        "fleet_id": fleet_id, "fleet_name": f.name,
        "diesel_co2_per_km_kg": round(d_co2, 4),
        "ev_co2_per_km_kg": round(e_co2, 4),
        "annual_scope1_tons": round(annual_scope1, 1),
        "annual_ev_co2_tons": round(annual_ev_co2, 1),
        "annual_potential_saving_tons": round(annual_avoided, 1),
        "ev_penetration_pct": round((f.ev_vehicles / max(f.total_vehicles, 1)) * 100, 1),
    }
