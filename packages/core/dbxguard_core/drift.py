from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DriftFinding:
    path: str
    desired: Any
    actual: Any
    kind: str


def detect_drift(desired: Any, actual: Any, path: str = "") -> list[DriftFinding]:
    findings: list[DriftFinding] = []
    if isinstance(desired, dict) and isinstance(actual, dict):
        for key in sorted(set(desired) | set(actual)):
            child = f"{path}.{key}" if path else str(key)
            if key not in desired:
                findings.append(DriftFinding(child, None, actual[key], "UNMANAGED"))
            elif key not in actual:
                findings.append(DriftFinding(child, desired[key], None, "MISSING"))
            else:
                findings.extend(detect_drift(desired[key], actual[key], child))
        return findings
    if isinstance(desired, list) and isinstance(actual, list):
        if desired != actual:
            findings.append(DriftFinding(path, desired, actual, "MODIFIED"))
        return findings
    if desired != actual:
        findings.append(DriftFinding(path, desired, actual, "MODIFIED"))
    return findings
