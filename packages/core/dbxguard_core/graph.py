from __future__ import annotations

from collections import defaultdict, deque

from .models import GraphEdge, GraphNode, ImpactSummary


class DependencyGraph:
    """Deterministic downstream dependency graph."""

    def __init__(self) -> None:
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []
        self._downstream: dict[str, list[GraphEdge]] = defaultdict(list)

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)
        self._downstream[edge.source].append(edge)

    def blast_radius(self, start: str, max_depth: int = 15, min_confidence: float = 0.0) -> ImpactSummary:
        if start not in self.nodes:
            return ImpactSummary()
        queue = deque([(start, [start], 0)])
        visited = {start}
        by_type: dict[str, int] = defaultdict(int)
        critical: list[str] = []
        paths: list[list[str]] = []
        while queue:
            current, path, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for edge in self._downstream.get(current, []):
                if edge.confidence < min_confidence or edge.target in visited:
                    continue
                visited.add(edge.target)
                node = self.nodes.get(edge.target)
                new_path = [*path, edge.target]
                if node:
                    by_type[node.type.value] += 1
                    if node.criticality <= 1:
                        critical.append(node.id)
                paths.append(new_path)
                queue.append((edge.target, new_path, depth + 1))
        return ImpactSummary(total=max(0, len(visited)-1), by_type=dict(by_type), critical_assets=critical, paths=paths[:100])
