"""Graph store abstraction with a Neo4j-first, in-memory-fallback factory."""
from abc import ABC, abstractmethod

from ..config import get_settings


class GraphStore(ABC):
    @abstractmethod
    def load_seed(self) -> None:
        """(Re)load the seed graph into the store."""

    @abstractmethod
    def get_graph(self) -> tuple[list[dict], list[dict]]:
        """Return (nodes, edges) as plain dicts."""


def get_store() -> GraphStore:
    settings = get_settings()
    if settings.use_neo4j:
        from .neo4j_store import Neo4jStore

        return Neo4jStore()
    from .memory_store import MemoryStore

    return MemoryStore()
