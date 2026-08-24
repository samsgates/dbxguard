from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CapabilityMatrix:
    unity_catalog: bool = False
    jobs: bool = False
    warehouses: bool = False
    clusters: bool = False
    serving_endpoints: bool = False
    system_tables: dict[str, bool] = field(default_factory=dict)


class DatabricksConnector:
    """Read-only Databricks inventory connector using standard SDK authentication."""

    def __init__(self, client: Any | None = None) -> None:
        if client is None:
            try:
                from databricks.sdk import WorkspaceClient
            except ImportError as exc:
                raise RuntimeError(
                    "databricks-sdk is required for live workspace access. Install the project dependencies first."
                ) from exc
            client = WorkspaceClient()
        self.client = client

    def test_connection(self) -> dict[str, Any]:
        me = self.client.current_user.me()
        return {"ok": True, "user_name": getattr(me, "user_name", None), "id": getattr(me, "id", None)}

    def discover_capabilities(self) -> CapabilityMatrix:
        matrix = CapabilityMatrix()
        probes = [
            ("jobs", lambda: next(iter(self.client.jobs.list(limit=1)), None)),
            ("clusters", lambda: next(iter(self.client.clusters.list()), None)),
            ("warehouses", lambda: next(iter(self.client.warehouses.list()), None)),
            ("serving_endpoints", lambda: next(iter(self.client.serving_endpoints.list()), None)),
            ("unity_catalog", lambda: next(iter(self.client.catalogs.list()), None)),
        ]
        for attr, probe in probes:
            try:
                probe()
                setattr(matrix, attr, True)
            except Exception:
                setattr(matrix, attr, False)
        return matrix

    def inventory_jobs(self, limit: int = 1000) -> list[dict[str, Any]]:
        out = []
        for idx, job in enumerate(self.client.jobs.list(expand_tasks=True)):
            if idx >= limit:
                break
            out.append(job.as_dict())
        return out

    def inventory_catalogs(self, limit: int = 1000) -> list[dict[str, Any]]:
        out = []
        for idx, catalog in enumerate(self.client.catalogs.list()):
            if idx >= limit:
                break
            out.append(catalog.as_dict())
        return out
