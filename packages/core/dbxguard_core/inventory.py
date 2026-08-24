from __future__ import annotations

from typing import Any, Iterable

from .graph import DependencyGraph
from .models import GraphEdge, GraphNode, ResourceType


def graph_from_inventory(
    assets: Iterable[dict[str, Any]],
    dependencies: Iterable[dict[str, Any]],
) -> DependencyGraph:
    graph = DependencyGraph()
    for asset in assets:
        raw_type = str(asset.get("type", "UNKNOWN")).upper()
        resource_type = ResourceType(raw_type) if raw_type in ResourceType._value2member_map_ else ResourceType.UNKNOWN
        graph.add_node(GraphNode(
            id=str(asset["id"]),
            name=str(asset.get("name") or asset["id"]),
            type=resource_type,
            criticality=int(asset.get("criticality", 3)),
            metadata=dict(asset.get("metadata", {})),
        ))
    for dep in dependencies:
        graph.add_edge(GraphEdge(
            source=str(dep["source"]),
            target=str(dep["target"]),
            relationship=str(dep.get("relationship", "DEPENDS_ON")),
            confidence=float(dep.get("confidence", 1.0)),
        ))
    return graph
