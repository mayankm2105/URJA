from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db, Fleet
from schemas import PriorityItem, ChatRequest, ChatResponse
from services.ai_service import rank_electrification_priorities, generate_mock_response, call_gemini

router = APIRouter()


@router.get("/ai/priorities", response_model=List[PriorityItem])
def get_priorities(db: Session = Depends(get_db)):
    """AI-ranked electrification priorities based on carbon impact + readiness."""
    fleets = db.query(Fleet).all()
    fleet_dicts = [
        {
            "id": f.id, "name": f.name, "operator": f.operator,
            "asset_class": f.asset_class, "hub_city": f.hub_city,
            "total_vehicles": f.total_vehicles, "ev_vehicles": f.ev_vehicles,
            "diesel_vehicles": f.diesel_vehicles, "avg_daily_km": f.avg_daily_km,
            "avg_payload_tons": f.avg_payload_tons,
            "diesel_co2_per_km": 0.9,  # computed in service
            "lat": f.lat, "lon": f.lon,
        }
        for f in fleets
    ]
    ranked = rank_electrification_priorities(fleet_dicts)
    return [PriorityItem(**r) for r in ranked]
@router.post("/ai/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """AI chat: tries Gemini first, falls back to rule-based mock."""
    gemini_reply = await call_gemini(req.message, req.history or [], db)
    if gemini_reply:
        return ChatResponse(reply=gemini_reply, intent="gemini", data_refs=["live_ai"])

    mock = generate_mock_response(req.message, db)
    return ChatResponse(**mock)
