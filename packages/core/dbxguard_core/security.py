from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccessExposure:
    new_identities: int
    sensitive_objects: int
    broad_group: bool
    privilege: str
    score: float
    severity: str


def score_access_exposure(new_identities: int, sensitive_objects: int, privilege: str, broad_group: bool = False) -> AccessExposure:
    if new_identities < 0 or sensitive_objects < 0:
        raise ValueError("counts must be non-negative")
    privilege_weight = {
        "SELECT": 15,
        "MODIFY": 35,
        "CREATE": 40,
        "USE_CATALOG": 10,
        "USE_SCHEMA": 10,
        "OWN": 80,
        "ALL_PRIVILEGES": 90,
    }.get(privilege.upper(), 25)
    score = privilege_weight
    score += min(30, new_identities / 50)
    score += min(30, sensitive_objects * 2)
    if broad_group:
        score += 15
    score = min(100.0, score)
    severity = "CRITICAL" if score >= 80 else "HIGH" if score >= 60 else "MEDIUM" if score >= 40 else "MODERATE" if score >= 20 else "LOW"
    return AccessExposure(new_identities, sensitive_objects, broad_group, privilege.upper(), round(score, 2), severity)
