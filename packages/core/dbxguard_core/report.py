from __future__ import annotations

from .models import AnalysisResult


def render_markdown(result: AnalysisResult) -> str:
    lines = [
        "# DBXGuard Deployment Analysis",
        "",
        f"**Decision:** {result.decision.value}",
        f"**Risk:** {result.risk.score}/100 ({result.risk.severity.value})",
        f"**Confidence:** {result.risk.confidence:.0%}",
        f"**Environment:** {result.environment}",
        "",
        "## Blast radius",
        "",
        f"Affected assets: **{result.impact.total}**",
        f"Critical assets: **{len(result.impact.critical_assets)}**",
        "",
        "## Findings",
        "",
    ]
    if not result.findings:
        lines.append("No findings.")
    for finding in result.findings:
        lines.extend([
            f"### {finding.severity.value}: {finding.title}",
            "",
            f"Resource: `{finding.resource}`",
            "",
            finding.description,
            "",
        ])
        if finding.recommendation:
            lines.extend([f"Recommendation: {finding.recommendation}", ""])
    if result.policy_results:
        lines.extend(["## Policies", ""])
        for policy in result.policy_results:
            lines.append(f"- **{policy.action.value}** `{policy.policy}`. {policy.reason}")
    return "\n".join(lines).rstrip() + "\n"
