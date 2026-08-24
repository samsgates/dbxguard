from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Severity(StrEnum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Decision(StrEnum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    BLOCK = "BLOCK"


class ChangeOperation(StrEnum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    RENAME = "RENAME"
    TYPE_CHANGE = "TYPE_CHANGE"
    DROP_COLUMN = "DROP_COLUMN"
    ADD_COLUMN = "ADD_COLUMN"
    PERMISSION_CHANGE = "PERMISSION_CHANGE"
    COMPUTE_CHANGE = "COMPUTE_CHANGE"
    SCHEDULE_CHANGE = "SCHEDULE_CHANGE"
    DEPENDENCY_CHANGE = "DEPENDENCY_CHANGE"


class ResourceType(StrEnum):
    TABLE = "TABLE"
    COLUMN = "COLUMN"
    VIEW = "VIEW"
    JOB = "JOB"
    TASK = "TASK"
    PIPELINE = "PIPELINE"
    DASHBOARD = "DASHBOARD"
    WAREHOUSE = "WAREHOUSE"
    CLUSTER = "CLUSTER"
    MODEL = "MODEL"
    MODEL_VERSION = "MODEL_VERSION"
    SERVING_ENDPOINT = "SERVING_ENDPOINT"
    USER = "USER"
    GROUP = "GROUP"
    SERVICE_PRINCIPAL = "SERVICE_PRINCIPAL"
    REPOSITORY = "REPOSITORY"
    FILE = "FILE"
    UNKNOWN = "UNKNOWN"


class Evidence(BaseModel):
    id: str = Field(default_factory=lambda: f"E-{uuid4().hex[:10]}")
    source: str
    description: str
    confidence: float = Field(default=1.0, ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Change(BaseModel):
    id: str = Field(default_factory=lambda: f"CHG-{uuid4().hex[:10]}")
    resource: str
    resource_type: ResourceType = ResourceType.UNKNOWN
    operation: ChangeOperation
    property: str | None = None
    before: Any = None
    after: Any = None
    source_file: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class GraphNode(BaseModel):
    id: str
    type: ResourceType = ResourceType.UNKNOWN
    name: str
    criticality: int = Field(default=3, ge=0, le=3)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str = "DEPENDS_ON"
    confidence: float = Field(default=1.0, ge=0, le=1)
    evidence: list[Evidence] = Field(default_factory=list)


class ImpactSummary(BaseModel):
    total: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)
    critical_assets: list[str] = Field(default_factory=list)
    paths: list[list[str]] = Field(default_factory=list)


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: f"DBX-{uuid4().hex[:10].upper()}")
    category: str
    title: str
    severity: Severity
    confidence: float = Field(default=1.0, ge=0, le=1)
    resource: str
    change_id: str | None = None
    description: str
    affected_assets: list[str] = Field(default_factory=list)
    recommendation: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RiskDimensions(BaseModel):
    data: float = 0
    reliability: float = 0
    security: float = 0
    ai_ml: float = 0
    cost: float = 0
    compliance: float = 0


class RiskResult(BaseModel):
    score: float
    severity: Severity
    confidence: float
    dimensions: RiskDimensions


class PolicyResult(BaseModel):
    policy: str
    action: Decision
    matched: bool
    reason: str
    finding_ids: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: f"AN-{uuid4().hex[:12]}")
    environment: str = "development"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    changes: list[Change] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    impact: ImpactSummary = Field(default_factory=ImpactSummary)
    risk: RiskResult
    decision: Decision
    policy_results: list[PolicyResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
