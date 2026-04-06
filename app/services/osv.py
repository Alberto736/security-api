from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.services.http import request_with_retries

_ECOSYSTEM_MAP: dict[str, str] = {
    "npm": "npm",
    "pip": "PyPI",
    "maven": "Maven",
    "gradle": "Maven",
    "composer": "Packagist",
    "nuget": "NuGet",
    "rubygems": "RubyGems",
    "cargo": "crates.io",
    "golang": "Go",
    "docker": "Docker",
}


@dataclass(frozen=True)
class OsvFinding:
    cve_id: str
    severity: str = "UNKNOWN"
    score: float = 0.0


async def query_osv(client: httpx.AsyncClient, *, name: str, version: str | None, ecosystem: str) -> list[OsvFinding]:
    osv_ecosystem = _ECOSYSTEM_MAP.get(ecosystem.lower(), "")
    if not osv_ecosystem:
        return []

    payload: dict = {"package": {"name": name, "ecosystem": osv_ecosystem}}
    if version:
        payload["version"] = version

    async def _do() -> httpx.Response:
        return await client.post("https://api.osv.dev/v1/query", json=payload)

    try:
        resp = await request_with_retries(_do)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    out: list[OsvFinding] = []
    for v in data.get("vulns", []) or []:
        osv_id = v.get("id") or "UNKNOWN"
        aliases = v.get("aliases") or []
        cve_id = next((a for a in aliases if isinstance(a, str) and a.startswith("CVE-")), osv_id)

        # Extract severity and score from OSV data
        severity = "UNKNOWN"
        score = 0.0

        # Check database_specific severity if available
        db_specific = v.get("database_specific", {})
        if db_specific:
            severity = db_specific.get("severity", "UNKNOWN").upper()
            score = float(db_specific.get("cvss_score", 0.0))

        # Fallback to severity field if database_specific not available
        if severity == "UNKNOWN" and "severity" in v:
            severity = str(v["severity"]).upper()

        out.append(OsvFinding(cve_id=cve_id, severity=severity, score=score))
    return out
