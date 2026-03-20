from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.services.http import request_with_retries
from app.settings import Settings


@dataclass(frozen=True)
class NvdFinding:
    cve_id: str
    severity: str
    score: float


def _parse_severity(vuln: dict) -> tuple[str, float]:
    metrics = vuln.get("cve", {}).get("metrics", {}) or {}
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        arr = metrics.get(key) or []
        if not arr:
            continue
        first = arr[0] or {}
        data = (first.get("cvssData") or {}) if isinstance(first, dict) else {}
        severity = (data.get("baseSeverity") or first.get("baseSeverity") or "UNKNOWN").upper()
        score = float(data.get("baseScore") or 0.0)
        return severity, score
    return "UNKNOWN", 0.0


async def query_nvd(settings: Settings, client: httpx.AsyncClient, keyword: str) -> list[NvdFinding]:
    params = {"keywordSearch": keyword, "resultsPerPage": 50}
    headers = {"User-Agent": settings.user_agent}
    if settings.nvd_api_key:
        headers["apiKey"] = settings.nvd_api_key

    async def _do() -> httpx.Response:
        return await client.get(settings.nvd_api_url, params=params, headers=headers)

    try:
        resp = await request_with_retries(_do)
        resp.raise_for_status()
        payload = resp.json()
    except Exception:
        return []

    out: list[NvdFinding] = []
    for v in payload.get("vulnerabilities", []) or []:
        cve_id = ((v.get("cve") or {}).get("id")) or "UNKNOWN"
        severity, score = _parse_severity(v)
        out.append(NvdFinding(cve_id=cve_id, severity=severity, score=score))
    return out
