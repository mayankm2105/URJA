from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from database import get_db, Fleet, Route, EmissionRecord, NetZeroCommitment
from schemas import DashboardKPI

router = APIRouter()


@router.get("/dashboard", response_model=DashboardKPI)
def get_dashboard(db: Session = Depends(get_db)):
    total_fleets = db.query(Fleet).count()
    total_vehicles = db.query(func.sum(Fleet.total_vehicles)).scalar() or 0
    ev_vehicles = db.query(func.sum(Fleet.ev_vehicles)).scalar() or 0
    ev_penetration_pct = round((ev_vehicles / max(total_vehicles, 1)) * 100, 1)

    # YTD 2025 emissions (months 1-6)
    ytd = db.query(
        func.sum(EmissionRecord.scope1_tons),
        func.sum(EmissionRecord.scope3_tons),
        func.sum(EmissionRecord.ev_avoided_tons),
    ).filter(EmissionRecord.year == 2025).first()

    scope1_ytd = round(ytd[0] or 0, 1)
    scope3_ytd = round(ytd[1] or 0, 1)
    ev_avoided_ytd = round(ytd[2] or 0, 1)

    # Net zero progress derived from actual latest 12-month emission records vs commitment baseline
    recent_months = db.query(EmissionRecord.year, EmissionRecord.month)\
                      .distinct()\
                      .order_by(EmissionRecord.year.desc(), EmissionRecord.month.desc())\
                      .limit(12)\
                      .all()

    net_zero_progress_pct = 0.0
    if recent_months:
        month_filters = [and_(EmissionRecord.year == y, EmissionRecord.month == m) for y, m in recent_months]
        filter_cond = or_(*month_filters)

        ORG_TO_OPERATORS = {
            "Tata Group Industrial Fleet": ["Tata Steel"],
            "Mahindra Group Fleet": ["Mahindra Logistics"],
            "Adani Group Logistics": ["Adani Ports"],
            "E-Commerce India Delivery Cos": ["Flipkart", "Zomato", "Amazon India", "Delhivery", "Blue Dart"]
        }

        commitments = db.query(NetZeroCommitment).all()
        progress_pcts = []
        for c in commitments:
            operators = ORG_TO_OPERATORS.get(c.organization, [])
            current_total = db.query(func.sum(EmissionRecord.scope1_tons + EmissionRecord.scope3_tons))\
                              .join(Fleet)\
                              .filter(Fleet.operator.in_(operators))\
                              .filter(filter_cond)\
                              .scalar() or 0
            baseline_total = c.baseline_scope1_tons + c.baseline_scope3_tons
            if baseline_total > 0:
                progress = 1 - (current_total / baseline_total)
                progress_pcts.append(progress)
        
        if progress_pcts:
            net_zero_progress_pct = round((sum(progress_pcts) / len(progress_pcts)) * 100, 1)

    # Routes
    total_routes = db.query(Route).count()
    electrified = db.query(Route).filter(Route.is_electrified == True).count()

    # Top priority fleet (highest diesel vehicles * avg daily km = highest emission potential)
    top_fleet = db.query(Fleet).order_by(
        (Fleet.diesel_vehicles * Fleet.avg_daily_km).desc()
    ).first()
    top_priority = top_fleet.name if top_fleet else "—"

    # Carbon saved vs target
    carbon_saved_vs_target = round((ev_avoided_ytd / max(scope1_ytd, 1)) * 100, 1)

    return DashboardKPI(
        total_fleets=total_fleets,
        total_vehicles=total_vehicles,
        ev_penetration_pct=ev_penetration_pct,
        scope1_ytd_tons=scope1_ytd,
        scope3_ytd_tons=scope3_ytd,
        ev_avoided_ytd_tons=ev_avoided_ytd,
        net_zero_progress_pct=net_zero_progress_pct,
        routes_electrified=electrified,
        total_routes=total_routes,
        top_priority_fleet=top_priority,
        carbon_saved_vs_target_pct=carbon_saved_vs_target,
    )
