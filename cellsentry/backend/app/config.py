"""Application settings, loaded from environment / .env."""
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.neo4j_uri = os.getenv("NEO4J_URI", "").strip()
        self.neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j").strip()
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "").strip()
        self.graph_backend = os.getenv("GRAPH_BACKEND", "auto").strip().lower()
        self.cors_origins = [
            o.strip()
            for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
            if o.strip()
        ]
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        # Models — default to Opus 4.8; switch to claude-haiku-4-5 / claude-sonnet-4-6
        # to cut cost if you process the full corpus live.
        self.extraction_model = os.getenv("EXTRACTION_MODEL", "claude-opus-4-8").strip()
        self.briefing_model = os.getenv("BRIEFING_MODEL", "claude-opus-4-8").strip()

    @property
    def use_neo4j(self) -> bool:
        if self.graph_backend == "neo4j":
            return True
        if self.graph_backend == "memory":
            return False
        # auto: use Neo4j only if it's actually configured
        return bool(self.neo4j_uri and self.neo4j_password)


@lru_cache
def get_settings() -> Settings:
    return Settings()
