"""Neo4j-backed graph store (Aura or self-hosted).

Nodes are :Entity, relationships are :SUPPLIES. The `country_shares` dict is
stored as a JSON string because Neo4j cannot store nested maps as properties.
"""
from __future__ import annotations

import json

from neo4j import GraphDatabase

from ..config import get_settings
from .seed import SEED_EDGES, SEED_NODES
from .store import GraphStore


def _encode_shares(shares: dict | None) -> str | None:
    return json.dumps(shares) if shares else None


def _decode_shares(value):
    if not value:
        return None
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return None


class Neo4jStore(GraphStore):
    def __init__(self) -> None:
        s = get_settings()
        self._driver = GraphDatabase.driver(
            s.neo4j_uri, auth=(s.neo4j_user, s.neo4j_password)
        )

    def close(self) -> None:
        self._driver.close()

    def load_seed(self) -> None:
        with self._driver.session() as session:
            session.run("MATCH (n:Entity) DETACH DELETE n")
            for n in SEED_NODES:
                session.run(
                    "CREATE (e:Entity $props)",
                    props={
                        "id": n["id"],
                        "label": n["label"],
                        "type": n["type"],
                        "tier": n.get("tier"),
                        "country": n.get("country"),
                        "country_shares": _encode_shares(n.get("country_shares")),
                    },
                )
            for e in SEED_EDGES:
                session.run(
                    "MATCH (a:Entity {id: $s}), (b:Entity {id: $t}) "
                    "CREATE (a)-[r:SUPPLIES {type: $type, dependency: $dependency, "
                    "buffer_days: $buffer_days}]->(b)",
                    s=e["source"],
                    t=e["target"],
                    type=e.get("type", "supplies"),
                    dependency=e.get("dependency", 1.0),
                    buffer_days=e.get("buffer_days", 0.0),
                )

    def get_graph(self) -> tuple[list[dict], list[dict]]:
        with self._driver.session() as session:
            nodes = []
            for rec in session.run("MATCH (n:Entity) RETURN n"):
                n = dict(rec["n"])
                if n.get("country_shares"):
                    n["country_shares"] = _decode_shares(n["country_shares"])
                nodes.append(n)
            edges = [
                dict(rec)
                for rec in session.run(
                    "MATCH (a:Entity)-[r:SUPPLIES]->(b:Entity) "
                    "RETURN a.id AS source, b.id AS target, r.type AS type, "
                    "r.dependency AS dependency, r.buffer_days AS buffer_days"
                )
            ]
        return nodes, edges
