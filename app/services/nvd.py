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
        # Check both cvssData and direct level for CVSS v2
        if isinstance(first, dict):
            data = first.get("cvssData") or {}
            severity = (data.get("baseSeverity") or first.get("baseSeverity") or "UNKNOWN").upper()
            score = float(data.get("baseScore") or first.get("baseScore") or 0.0)
            if score > 0.0:  # Only return if we have a valid score
                return severity, score
    return "UNKNOWN", 0.0


async def query_nvd(settings: Settings, client: httpx.AsyncClient, package_name: str, version: str | None = None) -> list[NvdFinding]:
    """Query NVD for vulnerabilities in specific package and version."""
    # Build more specific query
    if version:
        # Search for package:version combination
        keyword = f"{package_name}:{version}"
    else:
        # Search for package name only
        keyword = package_name

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

        # Additional filtering: check if this CVE actually affects the package
        if _affects_package(v, package_name, version):
            out.append(NvdFinding(cve_id=cve_id, severity=severity, score=score))

    return out


def _affects_package(vulnerability: dict, package_name: str, version: str | None) -> bool:
    """Check if CVE actually affects the specific package version."""
    cve_data = vulnerability.get("cve", {})

    # Check descriptions for package name
    descriptions = cve_data.get("descriptions", [])
    for desc in descriptions:
        if package_name.lower() in desc.get("value", "").lower():
            return True

    # Check affected versions if available
    metrics = cve_data.get("metrics", {})
    for metric_type in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if metric_type in metrics:
            for metric in metrics[metric_type]:
                cvss_data = metric.get("cvssData", {})
                affected_version = cvss_data.get("version")
                if affected_version and version:
                    # Simple version comparison - could be enhanced with semantic versioning
                    if affected_version == version:
                        return True

    # If no specific version info, assume it might affect
    return True
