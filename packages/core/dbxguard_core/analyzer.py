from __future__ import annotations

from typing import Iterable

from dbxguard_policy.engine import PolicyEngine
from .graph import DependencyGraph
from .models import AnalysisResult, Change, ChangeOperation, Evidence, Finding, ImpactSummary, Severity
from .risk import RiskEngine


class Analyzer:
    def __init__(self, graph: DependencyGraph | None = None, policy_engine: PolicyEngine | None = None) -> None:
        self.graph = graph or DependencyGraph()
        self.policy_engine = policy_engine or PolicyEngine([])
        self.risk_engine = RiskEngine()

    def _findings_for_change(self, change: Change, impact: ImpactSummary) -> list[Finding]:
        findings: list[Finding] = []
        affected = [path[-1] for path in impact.paths if path]
        evidence = list(change.evidence)
        if change.operation in {ChangeOperation.DELETE, ChangeOperation.DROP_COLUMN}:
            findings.append(Finding(category="DATA", title="Destructive data change", severity=Severity.CRITICAL,
                confidence=0.98, resource=change.resource, change_id=change.id,
                description=f"{change.operation.value} may break downstream consumers.", affected_assets=affected,
                recommendation="Use a compatibility migration, migrate consumers, then remove the old object.", evidence=evidence))
        elif change.operation == ChangeOperation.TYPE_CHANGE:
            findings.append(Finding(category="DATA", title="Potentially incompatible type change", severity=Severity.HIGH,
                confidence=0.94, resource=change.resource, change_id=change.id,
                description=f"Type changed from {change.before!r} to {change.after!r}.", affected_assets=affected,
                recommendation="Introduce a compatible field/version and migrate consumers before removal.", evidence=evidence))
        elif change.operation == ChangeOperation.PERMISSION_CHANGE:
            findings.append(Finding(category="SECURITY", title="Permission surface changed", severity=Severity.HIGH,
                confidence=0.85, resource=change.resource, change_id=change.id,
                description="The proposed change modifies effective access and requires review.", affected_assets=affected,
                recommendation="Review grants, broad groups, sensitive tags and least-privilege scope.", evidence=evidence))
        elif change.operation == ChangeOperation.COMPUTE_CHANGE:
            before = change.before if isinstance(change.before,(int,float)) else None
            after = change.after if isinstance(change.after,(int,float)) else None
            severity = Severity.HIGH if before and after and after > before*2 else Severity.MEDIUM
            findings.append(Finding(category="COST", title="Compute configuration changed", severity=severity,
                confidence=0.8, resource=change.resource, change_id=change.id,
                description=f"Compute-related property {change.property or ''} changed.", affected_assets=affected,
                recommendation="Compare proposed capacity with historical utilization and budget thresholds.", evidence=evidence))
        if impact.critical_assets:
            findings.append(Finding(category="RELIABILITY", title="Critical downstream assets affected", severity=Severity.HIGH,
                confidence=0.9, resource=change.resource, change_id=change.id,
                description=f"The change reaches {len(impact.critical_assets)} Tier-0/Tier-1 asset(s).",
                affected_assets=impact.critical_assets,
                recommendation="Require owner approval and a verified rollback or compatibility plan.",
                evidence=[Evidence(source="graph", description="Critical dependency path", confidence=0.9)]))
        return findings

    def analyze(self, changes: Iterable[Change], environment: str = "development") -> AnalysisResult:
        changes = list(changes)
        findings: list[Finding] = []
        aggregate = ImpactSummary()
        seen_assets: set[str] = set()
        for change in changes:
            impact = self.graph.blast_radius(change.resource)
            aggregate.critical_assets.extend(x for x in impact.critical_assets if x not in aggregate.critical_assets)
            aggregate.paths.extend(impact.paths)
            for key,value in impact.by_type.items(): aggregate.by_type[key] = aggregate.by_type.get(key,0)+value
            for path in impact.paths: seen_assets.update(path[1:])
            findings.extend(self._findings_for_change(change, impact))
        aggregate.total = len(seen_assets)
        risk = self.risk_engine.calculate(findings, aggregate)
        policy_results = self.policy_engine.evaluate(changes, findings, environment, risk.score)
        decision = self.policy_engine.final_decision(policy_results, risk.score)
        return AnalysisResult(environment=environment, changes=changes, findings=findings, impact=aggregate,
                              risk=risk, decision=decision, policy_results=policy_results)
