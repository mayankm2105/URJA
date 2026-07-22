import httpx
import json
import logging
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"

def get_fallback_response(risk_tier: str) -> Dict[str, str]:
    urgency_map = {
        "Healthy": "Low",
        "Watch": "Medium",
        "Critical": "High"
    }
    urgency = urgency_map.get(risk_tier, "Medium")
    return {
        "explanation": f"The battery is currently in {risk_tier} condition based on recent degradation trends.",
        "likely_cause": "Standard operational wear and tear.",
        "recommendation": "Continue standard monitoring and planned maintenance.",
        "urgency": urgency
    }

def validate_keys(response_dict: Dict) -> bool:
    required_keys = {"explanation", "likely_cause", "recommendation", "urgency"}
    if not required_keys.issubset(response_dict.keys()):
        return False
    if response_dict.get("urgency") not in ["Low", "Medium", "High"]:
        return False
    return True

async def generate_explanation(rul_result: Dict[str, Any], anomaly_flags: Dict[str, bool]) -> Dict[str, str]:
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured.")

    payload_data = {
        "battery_id": rul_result.get("battery_id"),
        "current_soh": rul_result.get("current_soh"),
        "rul_cycles": rul_result.get("rul_cycles"),
        "confidence_band_cycles": rul_result.get("confidence_band_cycles"),
        "confidence_level": rul_result.get("confidence_level"),
        "risk_tier": rul_result.get("risk_tier"),
        "slope_blend": rul_result.get("slope_blend"),
        "temperature_anomaly": anomaly_flags.get("temperature_anomaly", False),
        "voltage_sag_anomaly": anomaly_flags.get("voltage_sag_anomaly", False)
    }

    system_prompt = (
        "You are a battery health diagnostic assistant. "
        "Return strict JSON only, no markdown fences, no preamble. "
        "Include exactly these keys: 'explanation' (2-3 sentence plain-language summary of the degradation state), "
        "'likely_cause' (short hypothesis grounded only in the given fields - do not invent causes), "
        "'recommendation' (1-2 actionable maintenance suggestions), "
        "'urgency' (must be exactly one of 'Low', 'Medium', 'High', and must be consistent with the provided risk_tier: Healthy->Low, Watch->Medium, Critical->High). "
        "Never output or recalculate any numeric SoH or RUL values, just explain the state."
    )

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async def make_request(prompt_addition=""):
        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt + prompt_addition},
                {"role": "user", "content": json.dumps(payload_data)}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(GROQ_API_URL, headers=headers, json=data)
            response.raise_for_status()
            return response.json()

    try:
        resp = await make_request()
        content = resp["choices"][0]["message"]["content"]
        result = json.loads(content)
        if validate_keys(result):
            return result
    except Exception as e:
        logger.warning(f"First LLM call failed: {e}")
        pass # Fall through to retry

    # Retry
    try:
        stricter_reminder = " Reminder: You MUST return strictly valid JSON with exact keys: explanation, likely_cause, recommendation, urgency. Urgency must be Low, Medium, or High."
        resp = await make_request(stricter_reminder)
        content = resp["choices"][0]["message"]["content"]
        result = json.loads(content)
        if validate_keys(result):
            return result
    except Exception as e:
        logger.warning(f"Second LLM call failed: {e}")

    # Fallback
    return get_fallback_response(rul_result.get("risk_tier", "Watch"))
