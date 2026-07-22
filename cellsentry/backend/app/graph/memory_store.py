"""In-memory graph store (NetworkX-free; just holds the seed). Zero infra."""
from __future__ import annotations

from .seed import SEED_EDGES, SEED_NODES
from .store import GraphStore


class MemoryStore(GraphStore):
    # class-level cache so the seed survives across requests in one process
    _nodes: list[dict] | None = None
    _edges: list[dict] | None = None

    def load_seed(self) -> None:
        MemoryStore._nodes = [dict(n) for n in SEED_NODES]
        MemoryStore._edges = [dict(e) for e in SEED_EDGES]

    def get_graph(self) -> tuple[list[dict], list[dict]]:
        if MemoryStore._nodes is None:
            self.load_seed()
        return (
            [dict(n) for n in MemoryStore._nodes or []],
            [dict(e) for e in MemoryStore._edges or []],
        )
