from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "analysis": {"lineage": {"enabled": True, "max_depth": 15}, "cost": {"enabled": True}, "security": {"enabled": True}, "ml": {"enabled": True}},
    "risk": {"thresholds": {"warning": 40, "approval": 60, "block": 80}},
    "ci": {"failure_mode": "closed"},
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str | Path = "dbxguard.yml") -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return DEFAULT_CONFIG
    return deep_merge(DEFAULT_CONFIG, yaml.safe_load(p.read_text()) or {})
