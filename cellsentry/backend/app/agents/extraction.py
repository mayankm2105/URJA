"""Signal extraction agent.

Maps free-text event copy to structured supply-chain entities via Claude
(forced tool-use — the most version-robust structured-output path). Falls back
to the corpus's embedded ground-truth mapping when no API key is configured.
"""
from __future__ import annotations

from ..config import get_settings
from ..graph.seed import SEED_NODES
from .llm import get_client

_MATERIALS = [n["label"] for n in SEED_NODES if n["type"] == "raw_material"]
_SUPPLIERS = [n["label"] for n in SEED_NODES if n["type"] == "supplier"]

_TOOL = {
    "name": "record_event",
    "description": "Record the structured supply-chain impact of a news event.",
    "input_schema": {
        "type": "object",
        "properties": {
            "materials": {
                "type": "array",
                "items": {"type": "string"},
                "description": f"Affected battery raw materials. Prefer these names: {_MATERIALS}",
            },
            "countries": {"type": "array", "items": {"type": "string"}},
            "suppliers": {
                "type": "array",
                "items": {"type": "string"},
                "description": f"Named companies. Known suppliers: {_SUPPLIERS}",
            },
            "event_type": {"type": "string"},
            "severity": {"type": "integer", "description": "0-100 supply-risk severity"},
            "direction": {
                "type": "string",
                "description": "one of supply_down, supply_up, price_up, price_down, compliance",
            },
            "rationale": {"type": "string"},
        },
        "required": ["materials", "countries", "suppliers", "event_type", "severity", "direction", "rationale"],
    },
}


def extract_from_text(text: str) -> dict | None:
    """Run the Claude extraction agent. Returns None if unavailable/failed."""
    client = get_client()
    if client is None:
        return None
    settings = get_settings()
    try:
        resp = client.messages.create(
            model=settings.extraction_model,
            max_tokens=1024,
            tools=[_TOOL],
            tool_choice={"type": "tool", "name": "record_event"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Extract the structured supply-chain impact from this event. "
                        "Map materials and suppliers to the known names where they match.\n\n"
                        f"EVENT:\n{text}"
                    ),
                }
            ],
        )
        for block in resp.content:
            if getattr(block, "type", None) == "tool_use":
                return dict(block.input)
    except Exception:
        return None
    return None


def resolve_event_mapping(event: dict) -> dict:
    """Structured mapping for a corpus event: Claude if a key is set, else embedded truth."""
    extracted = extract_from_text(event.get("body", ""))
    if extracted:
        return extracted
    return dict(event["extracted"])
