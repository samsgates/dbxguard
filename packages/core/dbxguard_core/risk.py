from __future__ import annotations

from statistics import mean

from .models import Finding, ImpactSummary, RiskDimensions, RiskResult, Severity

DEFAULT_WEIGHTS = {"data":0.25,"reliability":0.20,"security":0.20,"ai_ml":0.15,"cost":0.10,"compliance":0.10}
SEVERITY_SCORE = {Severity.LOW:15, Severity.MODERATE:30, Severity.MEDIUM:50, Severity.HIGH:75, Severity.CRITICAL:95}


def severity_for_score(score: float) -> Severity:
    if score >= 80: return Severity.CRITICAL
    if score >= 60: return Severity.HIGH
    if score >= 40: return Severity.MEDIUM
    if score >= 20: return Severity.MODERATE
    return Severity.LOW


class RiskEngine:
    def __init__(self, weights: dict[str,float] | None = None) -> None:
        self.weights = weights or DEFAULT_WEIGHTS

    def calculate(self, findings: list[Finding], impact: ImpactSummary) -> RiskResult:
        buckets = {"data":[],"reliability":[],"security":[],"ai_ml":[],"cost":[],"compliance":[]}
        confidences: list[float] = []
        mapping = {"DATA":"data","RELIABILITY":"reliability","SECURITY":"security","AI_ML":"ai_ml","COST":"cost","COMPLIANCE":"compliance"}
        for finding in findings:
            bucket = mapping.get(finding.category.upper(), "reliability")
            buckets[bucket].append(SEVERITY_SCORE[finding.severity])
            confidences.append(finding.confidence)
        values = {}
        for key, vals in buckets.items():
            values[key] = min(100.0, (max(vals)*0.75 + mean(vals)*0.25) if vals else 0.0)
        dims = RiskDimensions(**values)
        score = sum(getattr(dims,k)*w for k,w in self.weights.items())
        if impact.critical_assets: score = min(100, score + min(15, len(impact.critical_assets)*3))
        if impact.total > 25: score = min(100, score + min(10, impact.total/10))
        confidence = mean(confidences) if confidences else 1.0
        return RiskResult(score=round(score,2), severity=severity_for_score(score), confidence=round(confidence,3), dimensions=dims)
