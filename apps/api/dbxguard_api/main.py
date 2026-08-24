from __future__ import annotations

import json
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import PlainTextResponse, Response

from dbxguard_connectors.databricks import DatabricksConnector
from dbxguard_core.analyzer import Analyzer
from dbxguard_core.cost import estimate_scaled_compute_cost
from dbxguard_core.drift import detect_drift
from dbxguard_core.graph import DependencyGraph
from dbxguard_core.report import render_markdown
from dbxguard_parsers.sql import parse_sql
from dbxguard_policy.engine import PolicyEngine

from .db import AnalysisRecord, get_db, init_db
from .schemas import AnalyzeRequest, CostEstimateRequest, DriftRequest, SqlAnalyzeRequest
from .settings import get_settings

ANALYSES = Counter("dbxguard_analyses_total", "Total analyses")
ANALYSIS_SECONDS = Histogram("dbxguard_analysis_duration_seconds", "Analysis duration")
settings = get_settings()


def require_api_key(x_dbxguard_key: str | None = Header(default=None)) -> None:
    if settings.api_key and x_dbxguard_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing DBXGuard API key")


def load_default_policy_engine() -> PolicyEngine:
    try:
        return PolicyEngine.from_directory("policies")
    except Exception:
        return PolicyEngine([])


def build_graph(req) -> DependencyGraph:
    graph = DependencyGraph()
    for node in req.nodes:
        graph.add_node(node)
    for edge in req.edges:
        graph.add_edge(edge)
    return graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="DBXGuard API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health/live")
def live():
    return {"status": "ok"}


@app.get("/health/ready")
def ready():
    return {"status": "ready", "environment": settings.env}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def persist(result, db: Session) -> None:
    db.merge(AnalysisRecord(
        id=result.id,
        environment=result.environment,
        decision=result.decision.value,
        risk_score=str(result.risk.score),
        payload=result.model_dump_json(),
    ))
    db.commit()


@app.post("/api/v1/analyses", dependencies=[Depends(require_api_key)])
def analyze(req: AnalyzeRequest, db: Session = Depends(get_db)):
    with ANALYSIS_SECONDS.time():
        result = Analyzer(build_graph(req), load_default_policy_engine()).analyze(req.changes, req.environment)
        persist(result, db)
        ANALYSES.inc()
        return result


@app.post("/api/v1/analyses/sql", dependencies=[Depends(require_api_key)])
def analyze_sql(req: SqlAnalyzeRequest, db: Session = Depends(get_db)):
    try:
        changes = parse_sql(req.sql, "inline.sql", req.base_types)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"SQL parse failed: {exc}") from exc
    return analyze(AnalyzeRequest(environment=req.environment, changes=changes, nodes=req.nodes, edges=req.edges), db)


@app.get("/api/v1/analyses/{analysis_id}", dependencies=[Depends(require_api_key)])
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    row = db.get(AnalysisRecord, analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return json.loads(row.payload)


@app.get("/api/v1/analyses/{analysis_id}/report.md", response_class=PlainTextResponse, dependencies=[Depends(require_api_key)])
def get_analysis_report(analysis_id: str, db: Session = Depends(get_db)):
    from dbxguard_core.models import AnalysisResult
    row = db.get(AnalysisRecord, analysis_id)
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return render_markdown(AnalysisResult.model_validate_json(row.payload))


@app.get("/api/v1/analyses", dependencies=[Depends(require_api_key)])
def list_analyses(limit: int = 50, db: Session = Depends(get_db)):
    limit = min(max(limit, 1), 200)
    rows = db.scalars(select(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).limit(limit)).all()
    return [{"id": r.id, "environment": r.environment, "decision": r.decision,
             "risk_score": r.risk_score, "created_at": r.created_at} for r in rows]


@app.post("/api/v1/cost/estimate", dependencies=[Depends(require_api_key)])
def cost_estimate(req: CostEstimateRequest):
    return estimate_scaled_compute_cost(**req.model_dump()).__dict__


@app.post("/api/v1/drift", dependencies=[Depends(require_api_key)])
def drift(req: DriftRequest):
    return [finding.__dict__ for finding in detect_drift(req.desired, req.actual)]


@app.get("/api/v1/policies", dependencies=[Depends(require_api_key)])
def policies():
    engine = load_default_policy_engine()
    return [{"name": p.get("metadata", {}).get("name", p.get("__file__", "unnamed")),
             "kind": p.get("kind"), "apiVersion": p.get("apiVersion")} for p in engine.policies]


@app.get("/api/v1/workspaces/capabilities", dependencies=[Depends(require_api_key)])
def workspace_capabilities():
    try:
        return DatabricksConnector().discover_capabilities().__dict__
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Databricks connection unavailable: {exc}") from exc


@app.get("/api/v1/workspaces/test", dependencies=[Depends(require_api_key)])
def workspace_test():
    try:
        return DatabricksConnector().test_connection()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Databricks connection unavailable: {exc}") from exc
