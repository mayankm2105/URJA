from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Asset, BatteryCycle
from app.schemas import FleetSummaryResponse
from app.routers.assets import fetch_history_for_rul, fetch_population_slope
from app.services.rul_engine import compute_rul

router = APIRouter(prefix="/fleet", tags=["Fleet"])

@router.get("/summary", response_model=FleetSummaryResponse)
async def get_fleet_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset))
    assets = result.scalars().all()
    
    healthy = 0
    watch = 0
    critical = 0
    total_soh = 0.0
    valid_assets = 0
    
    pop_slope = await fetch_population_slope(db)
    
    for asset in assets:
        hist = await fetch_history_for_rul(asset.battery_id, db)
        if not hist:
            continue
            
        rul_res = compute_rul(asset.battery_id, hist, lambda: pop_slope)
        tier = rul_res["risk_tier"]
        
        if tier == "Healthy":
            healthy += 1
        elif tier == "Watch":
            watch += 1
        else:
            critical += 1
            
        total_soh += rul_res["current_soh"]
        valid_assets += 1
        
    return FleetSummaryResponse(
        total_assets=valid_assets,
        healthy_count=healthy,
        watch_count=watch,
        critical_count=critical,
        average_soh=total_soh / valid_assets if valid_assets > 0 else 0.0
    )
