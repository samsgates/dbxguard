from __future__ import annotations

import hashlib
import hmac
from dbxguard_core.models import AnalysisResult
from dbxguard_core.report import render_markdown


def verify_webhook_signature(secret: str, body: bytes, signature_header: str | None) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def github_check_conclusion(result: AnalysisResult) -> str:
    return "failure" if result.decision.value == "BLOCK" else "neutral" if result.decision.value in {"WARN", "REQUIRE_APPROVAL"} else "success"


def github_comment(result: AnalysisResult, max_chars: int = 60000) -> str:
    text = render_markdown(result)
    return text if len(text) <= max_chars else text[: max_chars - 40] + "\n\n_Report truncated._\n"
