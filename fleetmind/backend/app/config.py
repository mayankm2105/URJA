"""Application settings, loaded from environment / .env."""
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.cors_origins = [
            o.strip()
            for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
            if o.strip()
        ]
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        # Default to Opus 4.8; switch to claude-haiku-4-5 to cut cost when
        # briefing the whole fleet at once.
        self.briefing_model = os.getenv("BRIEFING_MODEL", "claude-opus-4-8").strip()
        # End-of-life threshold: an EV traction battery is retired at 80% SoH.
        self.eol_soh = float(os.getenv("EOL_SOH", "0.80"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
