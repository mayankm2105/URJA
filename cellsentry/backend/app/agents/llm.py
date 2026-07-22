"""Shared Claude client factory. Returns None when no API key is configured,
so callers can fall back to deterministic behaviour."""
from __future__ import annotations

from ..config import get_settings

try:
    import anthropic
except ImportError:  # pragma: no cover
    anthropic = None


def get_client():
    settings = get_settings()
    if not settings.anthropic_api_key or anthropic is None:
        return None
    try:
        return anthropic.Anthropic(api_key=settings.anthropic_api_key)
    except Exception:
        return None
