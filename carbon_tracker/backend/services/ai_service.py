"""
AI Service — Net Zero Priority & Carbon Intelligence
Rule-based scoring engine with Gemini API hook.
"""
import os
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from database import Fleet, EmissionRecord, NetZeroCommitment, Route
from services.carbon_engine import electrification_readiness_index, impact_score

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


# ─── Knowledge Base for AI Chat ──────────────────────────────────────────────
KNOWLEDGE_BASE = {
    "scope1": (
        "Scope 1 emissions are direct greenhouse gas emissions from sources "
        "owned or controlled by an organisation — primarily diesel combustion "
        "in fleet vehicles. For EV fleets this drops to near zero on-route."
    ),
    "scope3": (
        "Scope 3 emissions are indirect emissions across the value chain, "
        "including upstream fuel extraction, electricity generation, vehicle "
        "manufacturing, and supply chain transport. Electrification reduces "
        "Scope 3 but doesn't eliminate it — grid carbon intensity matters."
    ),
    "net_zero": (
        "Net Zero means achieving a balance between greenhouse gases emitted "
        "and removed from the atmosphere. India's industrial fleet sector must "
        "reach 30% EV penetration by 2030 (SIAM target). For SBTi-aligned "
        "targets, a 4.2% annual reduction rate follows the 1.5°C pathway."
    ),
    "fame": (
        "FAME-II (Faster Adoption and Manufacturing of Electric Vehicles) has "
        "disbursed over Rs 10,000 crore in incentives. TCO parity with diesel "
        "is approaching for many commercial use cases in India."
    ),
    "readiness": (
        "Fleet electrification readiness is scored 0-100 based on: current EV "
        "penetration (40%), route suitability — shorter daily km = better (30%), "
        "payload weight — lighter = easier (20%), and asset class (10%). "
        "Intra-plant logistics and last-mile delivery score highest."
    ),
    "india_grid": (
        "India's grid emission factor is 0.82 kg CO2e/kWh (CEA 2024). "
        "With 35% renewable penetration for EV charging, the effective carbon "
        "intensity drops significantly. By 2030, India targets 500 GW renewable "
        "capacity, which will further improve EV lifecycle emissions."
    ),
}


def generate_mock_response(message: str, db: Session) -> dict:
    """Rule-based AI response using live database values."""
    msg_lower = message.lower()

    # Pre-query common dashboard data
    try:
        ytd = db.query(
            func.sum(EmissionRecord.scope1_tons),
            func.sum(EmissionRecord.scope3_tons),
            func.sum(EmissionRecord.ev_avoided_tons),
        ).filter(EmissionRecord.year == 2025).first()
        scope1_ytd = round(ytd[0] or 0, 1)
        scope3_ytd = round(ytd[1] or 0, 1)
        ev_avoided_ytd = round(ytd[2] or 0, 1)
    except Exception:
        scope1_ytd, scope3_ytd, ev_avoided_ytd = 0.0, 0.0, 0.0

    if any(w in msg_lower for w in ["scope 1", "scope1", "direct emission"]):
        reply = f"**Scope 1 Emissions:**\n\n{KNOWLEDGE_BASE['scope1']}\n\n📊 Your fleet's current Scope 1 YTD (2025): **{scope1_ytd:,} tCO₂e**."
        intent = "scope1_query"

    elif any(w in msg_lower for w in ["scope 3", "scope3", "upstream", "supply chain"]):
        reply = f"**Scope 3 Emissions:**\n\n{KNOWLEDGE_BASE['scope3']}\n\n📊 Upstream Scope 3 contributes to the overall footprint. Your fleet's current Scope 3 YTD (2025): **{scope3_ytd:,} tCO₂e**."
        intent = "scope3_query"

    elif any(w in msg_lower for w in ["net zero", "target", "commitment", "2030", "2035"]):
        # Compute dynamic progress
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
                curr_tot = db.query(func.sum(EmissionRecord.scope1_tons + EmissionRecord.scope3_tons))\
                             .join(Fleet)\
                             .filter(Fleet.operator.in_(operators))\
                             .filter(filter_cond)\
                             .scalar() or 0
                base_tot = c.baseline_scope1_tons + c.baseline_scope3_tons
                if base_tot > 0:
                    progress_pcts.append(1 - (curr_tot / base_tot))
            if progress_pcts:
                net_zero_progress_pct = round((sum(progress_pcts) / len(progress_pcts)) * 100, 1)

        reply = f"**Net Zero Progress:**\n\n{KNOWLEDGE_BASE['net_zero']}\n\n🎯 Your organisation is **{net_zero_progress_pct}%** on track against the Net Zero trajectory."
        intent = "net_zero_query"

    elif any(w in msg_lower for w in ["priority", "next", "highest impact", "recommend", "electrif"]):
        fleets = db.query(Fleet).all()
        fleet_dicts = [
            {
                "id": f.id, "name": f.name, "operator": f.operator,
                "asset_class": f.asset_class, "hub_city": f.hub_city,
                "total_vehicles": f.total_vehicles, "ev_vehicles": f.ev_vehicles,
                "diesel_vehicles": f.diesel_vehicles, "avg_daily_km": f.avg_daily_km,
                "avg_payload_tons": f.avg_payload_tons,
                "lat": f.lat, "lon": f.lon,
            }
            for f in fleets
        ]
        ranked = rank_electrification_priorities(fleet_dicts)
        top_3 = ranked[:3]
        
        reply = "**Top 3 Electrification Priorities** (by impact score):\n\n"
        medals = ["🏆", "🥈", "🥉"]
        for idx, item in enumerate(top_3):
            reply += f"{idx+1}. {medals[idx]} **{item['fleet_name']}** — Impact: {item['impact_score']} | Potential: {item['potential_saving_tons']:,} tCO₂e/yr saved\n"
        reply += "\nThese are ranked by a composite score of carbon impact (50%), potential saving (30%), and readiness (20%)."
        intent = "priority_query"

    elif any(w in msg_lower for w in ["fame", "incentive", "subsidy", "policy"]):
        reply = f"**FAME-II Policy Context:**\n\n{KNOWLEDGE_BASE['fame']}\n\n💡 For your freight fleet, TCO parity with diesel is expected by FY2026 for routes under 200 km/day."
        intent = "policy_query"

    elif any(w in msg_lower for w in ["readiness", "ready", "score"]):
        fleets = db.query(Fleet).all()
        highest_f = None
        highest_ri = -1
        for f in fleets:
            ev_pct = (f.ev_vehicles / max(f.total_vehicles, 1)) * 100
            ri = electrification_readiness_index(ev_pct, f.avg_daily_km, f.avg_payload_tons, f.asset_class)
            if ri > highest_ri:
                highest_ri = ri
                highest_f = f.name
        
        reply = f"**Electrification Readiness Scoring:**\n\n{KNOWLEDGE_BASE['readiness']}\n\n📈 Your highest-readiness fleet: **{highest_f}** at **{highest_ri}/100**."
        intent = "readiness_query"

    elif any(w in msg_lower for w in ["grid", "electricity", "kwh", "renewable"]):
        reply = f"**India Grid Emissions:**\n\n{KNOWLEDGE_BASE['india_grid']}\n\n⚡ At 0.82 kg CO₂e/kWh with 35% renewable charging, your EVs already emit **68% less** than equivalent diesel trucks per km."
        intent = "grid_query"

    elif any(w in msg_lower for w in ["route", "map", "geospatial", "location"]):
        routes = db.query(Route).filter(Route.is_electrified == False).all()
        enriched = []
        for r in routes:
            monthly_co2 = (r.distance_km * r.trips_per_month * r.co2_per_km_kg) / 1000
            enriched.append({
                "name": r.name,
                "monthly_co2_tons": round(monthly_co2, 2),
                "trips_per_month": r.trips_per_month,
            })
        enriched.sort(key=lambda x: x["monthly_co2_tons"], reverse=True)
        top_routes = enriched[:3]
        
        reply = (
            "**Route-Level Carbon Analysis:**\n\n"
            "Your highest-emission routes by monthly CO₂:\n"
        )
        for tr in top_routes:
            reply += f"• **{tr['name']}**: {tr['monthly_co2_tons']:,} tCO₂e/month — {tr['trips_per_month']} trips/month\n"
        reply += "\n🗺️ View the full geospatial breakdown on the **Map** screen."
        intent = "route_query"

    else:
        reply = (
            "I'm your **Net Zero Carbon Intelligence Agent**. I can help you with:\n\n"
            "• 📊 **Scope 1 & 3 emissions** breakdown and trends\n"
            "• 🎯 **Net zero progress** vs your commitments\n"
            "• 🏆 **Top electrification priorities** by impact score\n"
            "• 🗺️ **Route-level carbon** analysis\n"
            "• ⚡ **Fleet readiness** scoring\n"
            "• 🏛️ **FAME-II policy** & incentives context\n\n"
            "What would you like to explore?"
        )
        intent = "general"

    return {
        "reply": reply,
        "intent": intent,
        "data_refs": ["emissions_api", "fleet_api", "routes_api"],
    }


async def call_gemini(message: str, history: list, db: Session = None) -> Optional[str]:
    """Call Gemini 1.5 Flash API if key is available."""
    if not GEMINI_API_KEY:
        return None
    try:
        import httpx
        context_str = ""
        if db:
            try:
                # Query dashboard KPIs for context
                total_fleets = db.query(Fleet).count()
                total_vehicles = db.query(func.sum(Fleet.total_vehicles)).scalar() or 0
                ev_vehicles = db.query(func.sum(Fleet.ev_vehicles)).scalar() or 0
                ev_penetration_pct = round((ev_vehicles / max(total_vehicles, 1)) * 100, 1)

                ytd = db.query(
                    func.sum(EmissionRecord.scope1_tons),
                    func.sum(EmissionRecord.scope3_tons),
                    func.sum(EmissionRecord.ev_avoided_tons),
                ).filter(EmissionRecord.year == 2025).first()
                scope1_ytd = round(ytd[0] or 0, 1)
                scope3_ytd = round(ytd[1] or 0, 1)
                ev_avoided_ytd = round(ytd[2] or 0, 1)

                # Net zero progress
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
                        curr_tot = db.query(func.sum(EmissionRecord.scope1_tons + EmissionRecord.scope3_tons))\
                                     .join(Fleet)\
                                     .filter(Fleet.operator.in_(operators))\
                                     .filter(filter_cond)\
                                     .scalar() or 0
                        base_tot = c.baseline_scope1_tons + c.baseline_scope3_tons
                        if base_tot > 0:
                            progress_pcts.append(1 - (curr_tot / base_tot))
                    if progress_pcts:
                        net_zero_progress_pct = round((sum(progress_pcts) / len(progress_pcts)) * 100, 1)

                # Top 3 priorities
                fleets = db.query(Fleet).all()
                fleet_dicts = [
                    {
                        "id": f.id, "name": f.name, "operator": f.operator,
                        "asset_class": f.asset_class, "hub_city": f.hub_city,
                        "total_vehicles": f.total_vehicles, "ev_vehicles": f.ev_vehicles,
                        "diesel_vehicles": f.diesel_vehicles, "avg_daily_km": f.avg_daily_km,
                        "avg_payload_tons": f.avg_payload_tons,
                        "lat": f.lat, "lon": f.lon,
                    }
                    for f in fleets
                ]
                ranked = rank_electrification_priorities(fleet_dicts)
                top_3 = ranked[:3]
                priorities_summary = ", ".join([f"{item['fleet_name']} (Impact Score: {item['impact_score']}, Savings: {item['potential_saving_tons']} t/yr)" for item in top_3])

                context_str = (
                    f"\nReal-time Fleet & Carbon Data:\n"
                    f"- Total Fleets: {total_fleets}, Total Vehicles: {total_vehicles}\n"
                    f"- EV Penetration: {ev_penetration_pct}%\n"
                    f"- YTD 2025 Scope 1: {scope1_ytd} tCO2e, Scope 3: {scope3_ytd} tCO2e, EV Avoided: {ev_avoided_ytd} tCO2e\n"
                    f"- Average Net Zero Progress: {net_zero_progress_pct}%\n"
                    f"- Top 3 Electrification Priorities: {priorities_summary}\n"
                )
            except Exception as ex:
                print(f"Error querying context for Gemini: {ex}")

        system_prompt = (
            "You are a Net Zero Carbon Intelligence AI agent for an Indian industrial EV fleet operator. "
            "You analyse Scope 1 and Scope 3 emissions, track net zero commitments, and recommend "
            "the highest-impact electrification priorities. Use specific data when possible. "
            "Be concise, data-driven, and use markdown formatting with emojis for clarity. "
            "Context: India's industrial EV penetration is <2.5% (SIAM FY2025). "
            "Grid emission factor: 0.82 kg CO2e/kWh. Target: 30% EV penetration by 2030. "
            f"{context_str}"
        )
        contents = []
        for h in history[-6:]:  # last 3 turns
            contents.append({"role": h.role, "parts": [{"text": h.content}]})
        contents.append({"role": "user", "parts": [{"text": message}]})

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
                json={
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "contents": contents,
                    "generationConfig": {"maxOutputTokens": 512, "temperature": 0.4},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None


def rank_electrification_priorities(fleets_data: list) -> list:
    """
    Rank fleets by combined impact score for next electrification priorities.
    fleets_data: list of dicts from DB
    """
    ranked = []
    for f in fleets_data:
        diesel_count = f.get("diesel_vehicles", 0)
        if diesel_count == 0:
            continue

        from services.carbon_engine import diesel_co2_per_km, ev_co2_per_km
        d_co2 = diesel_co2_per_km(f.get("avg_payload_tons", 10))
        e_co2 = ev_co2_per_km(f.get("avg_payload_tons", 10))

        ev_pct = (f.get("ev_vehicles", 0) / max(f.get("total_vehicles", 1), 1)) * 100
        annual_km = f.get("avg_daily_km", 0) * 365 * diesel_count
        annual_co2 = (annual_km * d_co2) / 1000
        potential = (annual_km * (d_co2 - e_co2)) / 1000


        ri = electrification_readiness_index(
            ev_pct,
            f.get("avg_daily_km", 150),
            f.get("avg_payload_tons", 10),
            f.get("asset_class", "freight"),
        )
        imp = impact_score(annual_co2, potential, ri)

        recommendations = {
            "intra-plant logistics": "Deploy BEV shunters immediately — 100% route electrification feasible within 18 months.",
            "last-mile delivery": "Transition to light commercial EVs (Tata ACE EV, Mahindra Treo) within 12 months.",
            "logistics": "Electrify depot-to-hub routes first; install 150kW DC fast chargers at hubs.",
            "freight": "Pilot Tata Ultra EV on Mumbai–Pune corridor; evaluate charging at NHAI plazas.",
            "construction": "Replace compactors and small dumpers first; target 20% electrification by FY2026.",
            "mining": "Deploy electric LHDs in underground sections; surface haul trucks in 3-year horizon.",
        }

        ranked.append({
            "fleet_id": f["id"],
            "fleet_name": f["name"],
            "operator": f["operator"],
            "asset_class": f["asset_class"],
            "hub_city": f["hub_city"],
            "ev_penetration_pct": round(ev_pct, 1),
            "annual_co2_tons": round(annual_co2, 1),
            "potential_saving_tons": round(potential, 1),
            "readiness_index": ri,
            "impact_score": imp,
            "recommendation": recommendations.get(f["asset_class"].lower(), "Conduct detailed feasibility study."),
            "lat": f.get("lat", 0),
            "lon": f.get("lon", 0),
        })

    ranked.sort(key=lambda x: x["impact_score"], reverse=True)
    for i, item in enumerate(ranked):
        item["rank"] = i + 1

    return ranked
