from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from dbxguard_core.models import Change, GraphEdge, GraphNode


class AnalyzeRequest(BaseModel):
    environment: str = "development"
    changes: list[Change]
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class SqlAnalyzeRequest(BaseModel):
    environment: str = "development"
    sql: str
    base_types: dict[str, str] = Field(default_factory=dict)
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class CostEstimateRequest(BaseModel):
    historical_monthly_cost: float
    current_capacity: float
    proposed_capacity: float
    runtime_ratio: float = 1.0
    schedule_ratio: float = 1.0
    confidence: float = 0.8


class DriftRequest(BaseModel):
    desired: Any
    actual: Any
