from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime
import os
import time
import requests

app = FastAPI()

MONGO_URL = os.environ.get("MONGO_URI")
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NOTIFY_SEVERITIES = {"CRITICAL", "HIGH"}

client = MongoClient(MONGO_URL)
db = client["security"]
inventario = db["inventario"]

def query_nvd(keyword):
    params = {"keywordSearch": keyword, "resultsPerPage": 50}
    try:
        response = requests.get(NVD_API_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("vulnerabilities", [])
    except:
        return []

def query_osv(name, version, ecosystem):
    ecosystem_map = {
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
    osv_ecosystem = ecosystem_map.get(ecosystem, "")
    if not osv_ecosystem:
        return []
    payload = {
        "version": version,
        "package": {"name": name, "ecosystem": osv_ecosystem}
    }
    try:
        response = requests.post("https://api.osv.dev/v1/query", json=payload, timeout=15)
        response.raise_for_status()
        return response.json().get("vulns", [])
    except:
        return []

def parse_severity(vuln):
    metrics = vuln.get("cve", {}).get("metrics", {})
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if key in metrics and metrics[key]:
            data = metrics[key][0].get("cvssData", {})
            return data.get("baseSeverity", "UNKNOWN").upper(), data.get("baseScore", 0.0)
    return "UNKNOWN", 0.0

@app.post("/inventario")
def recibir_inventario(data: dict):
    """Recibe dependencias, guarda en MongoDB y comprueba CVEs"""
    data["fecha"] = datetime.now().isoformat()
    inventario.replace_one({"repo": data["repo"]}, data, upsert=True)

    alerts = []
    for dep in data.get("dependencias", []):
        name = dep.get("name", "")
        version = dep.get("version", "")
        ecosystem = dep.get("ecosystem", "")
        print(f"  Checking: {name} {version}...")

        # Consulta NVD
        vulns_nvd = query_nvd(name)
        for v in vulns_nvd:
            severity, score = parse_severity(v)
            if severity not in NOTIFY_SEVERITIES:
                continue
            cve = v.get("cve", {})
            cve_id = cve.get("id", "UNKNOWN")
            if not any(a["cve_id"] == cve_id for a in alerts):
                alerts.append({
                    "repo": data["repo"],
                    "name": name,
                    "version": version,
                    "cve_id": cve_id,
                    "severity": severity,
                    "score": score,
                    "source": "NVD"
                })

        # Consulta OSV
        vulns_osv = query_osv(name, version, ecosystem)
        for v in vulns_osv:
            osv_id = v.get("id", "UNKNOWN")
            aliases = v.get("aliases", [])
            cve_id = next((a for a in aliases if a.startswith("CVE-")), osv_id)
            if not any(a["cve_id"] == cve_id for a in alerts):
                alerts.append({
                    "repo": data["repo"],
                    "name": name,
                    "version": version,
                    "cve_id": cve_id,
                    "severity": "HIGH",
                    "score": 7.0,
                    "source": "OSV"
                })

        time.sleep(1)

    if alerts:
        alerts.sort(key=lambda x: x["score"], reverse=True)
        print(f"[INFO] {len(alerts)} alertas encontradas")

    return {"status": "ok", "repo": data["repo"], "alertas": len(alerts)}

@app.get("/inventario")
def get_inventario():
    return list(inventario.find({}, {"_id": 0}))

@app.get("/inventario/{repo}")
def get_repo(repo: str):
    result = inventario.find_one({"repo": repo}, {"_id": 0})
    if not result:
        return {"error": "Repositorio no encontrado"}
    return result
