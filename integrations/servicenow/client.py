from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import httpx


@dataclass
class ServiceNowClient:
    instance_url: str
    username: str
    password: str
    timeout: float = 20.0

    def create_change_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = self.instance_url.rstrip("/") + "/api/now/table/change_request"
        response = httpx.post(url, auth=(self.username, self.password), json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
