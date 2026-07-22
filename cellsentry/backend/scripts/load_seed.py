"""Load the seed graph into the configured store (Neo4j or in-memory).

Usage (from the backend/ directory):
    python scripts/load_seed.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.graph.store import get_store  # noqa: E402


def main() -> None:
    store = get_store()
    store.load_seed()
    nodes, edges = store.get_graph()
    print(f"Seeded {len(nodes)} nodes and {len(edges)} edges into the configured store.")


if __name__ == "__main__":
    main()
