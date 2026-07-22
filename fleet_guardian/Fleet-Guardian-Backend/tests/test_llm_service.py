import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.llm_service import generate_explanation

@pytest.fixture
def dummy_rul_result():
    return {
        "battery_id": "SYN0001",
        "current_soh": 0.85,
        "rul_cycles": 50.0,
        "confidence_band_cycles": 10.0,
        "confidence_level": "asset_specific",
        "risk_tier": "Healthy",
        "slope_blend": -0.001
    }

@pytest.fixture
def dummy_anomaly_flags():
    return {
        "temperature_anomaly": False,
        "voltage_sag_anomaly": False
    }

@pytest.mark.asyncio
async def test_llm_parse_success(dummy_rul_result, dummy_anomaly_flags):
    # 12. Mock Groq API call, assert parses well-formed JSON
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "explanation": "Test explanation.",
                    "likely_cause": "Test cause.",
                    "recommendation": "Test recommendation.",
                    "urgency": "Low"
                })
            }
        }]
    }
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("app.services.llm_service.settings") as mock_settings:
        mock_settings.GROQ_API_KEY = "test_key"
        mock_post.return_value = mock_response
        
        result = await generate_explanation(dummy_rul_result, dummy_anomaly_flags)
        
        assert result["explanation"] == "Test explanation."
        assert result["urgency"] == "Low"

@pytest.mark.asyncio
async def test_llm_retry_and_fallback_malformed(dummy_rul_result, dummy_anomaly_flags):
    # 13. Mock malformed response. Assert retries once, then fallback.
    mock_response = MagicMock()
    # First response missing fields
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({"explanation": "Incomplete"})
            }
        }]
    }
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("app.services.llm_service.settings") as mock_settings:
        mock_settings.GROQ_API_KEY = "test_key"
        mock_post.return_value = mock_response
        
        result = await generate_explanation(dummy_rul_result, dummy_anomaly_flags)
        
        assert mock_post.call_count == 2
        assert "explanation" in result
        assert "likely_cause" in result
        assert "recommendation" in result
        assert result["urgency"] == "Low" # Matches "Healthy" tier in dummy_rul_result

@pytest.mark.asyncio
async def test_llm_exception_fallback(dummy_rul_result, dummy_anomaly_flags):
    # 14. Mock exception/timeout, assert no unhandled exception, returns fallback
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("app.services.llm_service.settings") as mock_settings:
        mock_settings.GROQ_API_KEY = "test_key"
        mock_post.side_effect = Exception("Timeout")
        
        result = await generate_explanation(dummy_rul_result, dummy_anomaly_flags)
        
        assert mock_post.call_count == 2 # Tries again on first failure
        assert result["urgency"] == "Low"

@pytest.mark.asyncio
async def test_llm_payload_whitelist(dummy_rul_result, dummy_anomaly_flags):
    # 15. Assert payload sent contains only whitelisted fields
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "explanation": "E", "likely_cause": "L", "recommendation": "R", "urgency": "Low"
                })
            }
        }]
    }
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("app.services.llm_service.settings") as mock_settings:
        mock_settings.GROQ_API_KEY = "test_key"
        mock_post.return_value = mock_response
        
        # Add a malicious extra field to dummy data
        dummy_rul_result["voltage"] = [1.0, 2.0]
        
        await generate_explanation(dummy_rul_result, dummy_anomaly_flags)
        
        # Inspect called arguments
        call_kwargs = mock_post.call_args.kwargs
        sent_json = call_kwargs["json"]
        user_message = sent_json["messages"][1]["content"]
        sent_data = json.loads(user_message)
        
        assert "voltage" not in sent_data
        assert "battery_id" in sent_data
        assert "current_soh" in sent_data
