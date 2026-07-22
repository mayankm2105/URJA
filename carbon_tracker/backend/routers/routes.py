from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db, Route
from schemas import RouteOut

router = APIRouter()


@router.get("/routes", response_model=List[RouteOut])
def get_routes(is_electrified: Optional[bool] = None, db: Session = Depends(get_db)):
    query = db.query(Route)
    if is_electrified is not None:
        query = query.filter(Route.is_electrified == is_electrified)
    routes = query.all()
    result = []
    for r in routes:
        monthly_co2 = (r.distance_km * r.trips_per_month * r.co2_per_km_kg) / 1000
        ev_monthly_co2 = (r.distance_km * r.trips_per_month * r.ev_co2_per_km_kg) / 1000
        potential_saving = max(0, monthly_co2 - ev_monthly_co2)

        out = RouteOut(
            id=r.id, fleet_id=r.fleet_id, name=r.name,
            origin_city=r.origin_city, dest_city=r.dest_city,
            origin_lat=r.origin_lat, origin_lon=r.origin_lon,
            dest_lat=r.dest_lat, dest_lon=r.dest_lon,
            distance_km=r.distance_km, trips_per_month=r.trips_per_month,
            vehicle_type=r.vehicle_type, payload_tons=r.payload_tons,
            co2_per_km_kg=r.co2_per_km_kg, ev_co2_per_km_kg=r.ev_co2_per_km_kg,
            is_electrified=r.is_electrified,
            monthly_co2_tons=round(monthly_co2, 2),
            potential_saving_tons=round(potential_saving, 2),
        )
        result.append(out)
    return result


@router.get("/routes/top-emitters")
def get_top_emitting_routes(limit: int = 10, db: Session = Depends(get_db)):
    """Routes with the highest monthly CO2 emissions."""
    routes = db.query(Route).filter(Route.is_electrified == False).all()
    enriched = []
    for r in routes:
        monthly_co2 = (r.distance_km * r.trips_per_month * r.co2_per_km_kg) / 1000
        potential = (r.distance_km * r.trips_per_month * (r.co2_per_km_kg - r.ev_co2_per_km_kg)) / 1000
        enriched.append({
            "id": r.id, "name": r.name, "origin_city": r.origin_city, "dest_city": r.dest_city,
            "distance_km": r.distance_km, "monthly_co2_tons": round(monthly_co2, 2),
            "potential_saving_tons": round(potential, 2),
            "origin_lat": r.origin_lat, "origin_lon": r.origin_lon,
            "dest_lat": r.dest_lat, "dest_lon": r.dest_lon,
            "is_electrified": r.is_electrified,
        })
    enriched.sort(key=lambda x: x["monthly_co2_tons"], reverse=True)
    return enriched[:limit]


@router.get("/carbon/validation")
def carbon_validation(db: Session = Depends(get_db)):
    """Carbon tracking accuracy vs metered fuel (PS3 evaluation metric #5)."""
    from services.carbon_validation import validate

    rows = [
        {
            "id": r.id,
            "name": r.name,
            "origin_city": r.origin_city,
            "dest_city": r.dest_city,
            "distance_km": r.distance_km,
            "trips_per_month": r.trips_per_month,
            "payload_tons": r.payload_tons,
            "is_electrified": r.is_electrified,
        }
        for r in db.query(Route).all()
    ]
    return validate(rows)
