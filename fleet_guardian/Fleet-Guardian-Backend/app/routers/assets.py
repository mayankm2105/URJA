from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict
import time
import asyncio

from app.config import settings

from app.database import get_db
from app.models import Asset, BatteryCycle
from app.schemas import AssetBase, HealthResponse, RecommendationResponse, BatteryCycleResponse, ErrorResponse
from app.services.rul_engine import compute_rul, temperature_anomaly, voltage_sag_anomaly, get_population_median_slope
from app.services.llm_service import generate_explanation
from app.exceptions import NotFoundError

router = APIRouter(prefix="/assets", tags=["Assets"])

_cached_pop_slope = None
_cached_pop_slope_time = 0.0
_pop_slope_lock = asyncio.Lock()

async def fetch_population_slope(db: AsyncSession) -> float:
    global _cached_pop_slope, _cached_pop_slope_time
    now = time.time()
    
    if _cached_pop_slope is not None and (now - _cached_pop_slope_time) < settings.POP_SLOPE_CACHE_TTL_SECONDS:
        return _cached_pop_slope

    async with _pop_slope_lock:
        now = time.time()
        if _cached_pop_slope is not None and (now - _cached_pop_slope_time) < settings.POP_SLOPE_CACHE_TTL_SECONDS:
            return _cached_pop_slope

    result = await db.execute(select(BatteryCycle).order_by(BatteryCycle.battery_id, BatteryCycle.cycle))
    cycles = result.scalars().all()
    
    all_histories = {}
    for c in cycles:
        if c.battery_id not in all_histories:
            all_histories[c.battery_id] = {'cycles': [], 'soh': []}
        all_histories[c.battery_id]['cycles'].append(c.cycle)
        all_histories[c.battery_id]['soh'].append(c.soh)

    _cached_pop_slope = get_population_median_slope(all_histories)
    _cached_pop_slope_time = now
    return _cached_pop_slope

@router.post("/invalidate-cache")
async def invalidate_population_slope_cache():
    global _cached_pop_slope, _cached_pop_slope_time
    async with _pop_slope_lock:
        _cached_pop_slope = None
        _cached_pop_slope_time = 0.0
    return {"status": "cache invalidated"}

async def fetch_history_for_rul(battery_id: str, db: AsyncSession) -> Dict[str, list]:
    result = await db.execute(select(BatteryCycle).where(BatteryCycle.battery_id == battery_id).order_by(BatteryCycle.cycle))
    cycles = result.scalars().all()
    if not cycles:
        return None
    
    return {
        'cycles': [c.cycle for c in cycles],
        'soh': [c.soh for c in cycles],
        'temperature': [c.temperature for c in cycles],
        'voltage': [c.voltage for c in cycles]
    }

@router.get("", response_model=List[AssetBase])
async def list_assets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset))
    assets = result.scalars().all()
    
    response = []
    for asset in assets:
        hist = await fetch_history_for_rul(asset.battery_id, db)
        if not hist:
            continue
        
        pop_slope = await fetch_population_slope(db)
        rul_res = compute_rul(asset.battery_id, hist, lambda: pop_slope)
        
        response.append(AssetBase(
            battery_id=asset.battery_id,
            display_name=asset.display_name,
            current_soh=rul_res["current_soh"],
            risk_tier=rul_res["risk_tier"],
            last_updated_cycle=rul_res["current_cycle"]
        ))
    return response

@router.get("/{battery_id}/health", response_model=HealthResponse, responses={404: {"model": ErrorResponse}})
async def get_asset_health(battery_id: str, db: AsyncSession = Depends(get_db)):
    hist = await fetch_history_for_rul(battery_id, db)
    if not hist:
        raise NotFoundError(detail=f"Asset {battery_id} not found")

    pop_slope = await fetch_population_slope(db)
    rul_res = compute_rul(battery_id, hist, lambda: pop_slope)
    
    rul_res["temperature_anomaly"] = temperature_anomaly(hist["temperature"])
    rul_res["voltage_sag_anomaly"] = voltage_sag_anomaly(hist["voltage"])
    
    return HealthResponse(**rul_res)

@router.get("/{battery_id}/recommendation", response_model=RecommendationResponse, responses={404: {"model": ErrorResponse}})
async def get_asset_recommendation(battery_id: str, db: AsyncSession = Depends(get_db)):
    hist = await fetch_history_for_rul(battery_id, db)
    if not hist:
        raise NotFoundError(detail=f"Asset {battery_id} not found")

    pop_slope = await fetch_population_slope(db)
    rul_res = compute_rul(battery_id, hist, lambda: pop_slope)
    
    t_anom = temperature_anomaly(hist["temperature"])
    v_anom = voltage_sag_anomaly(hist["voltage"])
    rul_res["temperature_anomaly"] = t_anom
    rul_res["voltage_sag_anomaly"] = v_anom
    
    anomaly_flags = {
        "temperature_anomaly": t_anom,
        "voltage_sag_anomaly": v_anom
    }
    
    explanation = await generate_explanation(rul_res, anomaly_flags)
    rul_res.update(explanation)
    
    return RecommendationResponse(**rul_res)

@router.get("/{battery_id}/history", response_model=List[BatteryCycleResponse], responses={404: {"model": ErrorResponse}})
async def get_asset_history(battery_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BatteryCycle).where(BatteryCycle.battery_id == battery_id).order_by(BatteryCycle.cycle))
    cycles = result.scalars().all()
    if not cycles:
        raise NotFoundError(detail=f"Asset {battery_id} not found")
        
    return cycles
