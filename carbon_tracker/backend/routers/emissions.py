from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from database import get_db, EmissionRecord, Fleet, NetZeroCommitment, Supplier
from schemas import EmissionPoint, CommitmentOut, SupplierOut

router = APIRouter()


@router.get("/emissions/timeseries", response_model=List[EmissionPoint])
def get_emissions_timeseries(
    fleet_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        EmissionRecord.year,
        EmissionRecord.month,
        func.sum(EmissionRecord.scope1_tons).label("scope1"),
        func.sum(EmissionRecord.scope3_tons).label("scope3"),
        func.sum(EmissionRecord.ev_avoided_tons).label("avoided"),
        func.sum(EmissionRecord.target_tons).label("target"),
    )
    if fleet_id:
        query = query.filter(EmissionRecord.fleet_id == fleet_id)

    query = query.group_by(EmissionRecord.year, EmissionRecord.month)
    query = query.order_by(EmissionRecord.year, EmissionRecord.month)
    results = query.all()

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    return [
        EmissionPoint(
            year=r.year, month=r.month,
            scope1_tons=round(r.scope1, 1),
            scope3_tons=round(r.scope3, 1),
            ev_avoided_tons=round(r.avoided, 1),
            target_tons=round(r.target, 1),
            label=f"{months[r.month - 1]} {r.year}",
        )
        for r in results
    ]


@router.get("/emissions/by-fleet")
def get_emissions_by_fleet(year: int = 2025, db: Session = Depends(get_db)):
    """Emissions breakdown per fleet for the given year."""
    results = db.query(
        Fleet.name, Fleet.asset_class, Fleet.hub_city,
        func.sum(EmissionRecord.scope1_tons).label("scope1"),
        func.sum(EmissionRecord.scope3_tons).label("scope3"),
        func.sum(EmissionRecord.ev_avoided_tons).label("avoided"),
    ).join(EmissionRecord, Fleet.id == EmissionRecord.fleet_id)\
     .filter(EmissionRecord.year == year)\
     .group_by(Fleet.id).all()

    return [
        {
            "fleet_name": r.name, "asset_class": r.asset_class, "hub_city": r.hub_city,
            "scope1_tons": round(r.scope1 or 0, 1),
            "scope3_tons": round(r.scope3 or 0, 1),
            "ev_avoided_tons": round(r.avoided or 0, 1),
            "total_tons": round((r.scope1 or 0) + (r.scope3 or 0), 1),
        }
        for r in results
    ]


@router.get("/emissions/by-asset-class")
def get_emissions_by_asset_class(year: int = 2025, db: Session = Depends(get_db)):
    """Aggregate Scope 1 & 3 by asset class."""
    results = db.query(
        Fleet.asset_class,
        func.count(func.distinct(Fleet.id)).label("fleet_count"),
        func.sum(EmissionRecord.scope1_tons).label("scope1"),
        func.sum(EmissionRecord.scope3_tons).label("scope3"),
        func.sum(EmissionRecord.ev_avoided_tons).label("avoided"),
    ).join(EmissionRecord, Fleet.id == EmissionRecord.fleet_id)\
     .filter(EmissionRecord.year == year)\
     .group_by(Fleet.asset_class)\
     .order_by(func.sum(EmissionRecord.scope1_tons).desc()).all()

    return [
        {
            "asset_class": r.asset_class,
            "fleet_count": r.fleet_count,
            "scope1_tons": round(r.scope1 or 0, 1),
            "scope3_tons": round(r.scope3 or 0, 1),
            "ev_avoided_tons": round(r.avoided or 0, 1),
        }
        for r in results
    ]


@router.get("/commitments", response_model=List[CommitmentOut])
def get_commitments(db: Session = Depends(get_db)):
    return db.query(NetZeroCommitment).all()


@router.get("/suppliers", response_model=List[SupplierOut])
def get_suppliers(db: Session = Depends(get_db)):
    """Supply chain risk & carbon intensity data."""
    return db.query(Supplier).all()
