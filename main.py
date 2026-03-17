from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime
import os
import time
import requests

app = FastAPI()

MONGO_URL = os.environ.get("MONGO_URL")
TEAMS_WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_URL")
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

def parse_severity(vuln):
    metrics = vuln.get("cve", {}).get("metrics", {})
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if key in metrics and metrics[key]:
            data = metrics[key][0].get("cvssData", {})
            return data.get("baseSeverity", "UNKNOWN").upper(), data.get("baseScore", 0.0)
    return "UNKNOWN", 0.0

def send_to_teams(alerts):
    if not TEAMS_WEBHOOK_URL:
        print("TEAMS_WEBHOOK_URL no configurada")
        return

    critical = sum(1 for a in alerts if a["severity"] == "CRITICAL")
    high = sum(1 for a in alerts if a["severity"] == "HIGH")

    facts = []
    for a in alerts[:15]:
        emoji = "🔴" if a["severity"] == "CRITICAL" else "🟠"
        facts.append({
            "type": "FactSet",
            "separator": True,
            "facts": [
                {"title": "CVE", "value": a["cve_id"]},
                {"title": "Repositorio", "value": a["repo"]},
                {"title": "Tecnología", "value": f"{a['name']} {a['version']}"},
                {"title": "Severidad", "value": f"{emoji} {a['severity']} (CVSS {a['score']})"},
            ]
        })

    payload = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "Container",
                        "style": "attention" if critical > 0 else "warning",
                        "items": [
                            {"type": "TextBlock", "text": "🔐 Nuevas Vulnerabilidades Detectadas",
                             "weight": "Bolder", "size": "Large", "color": "Light"},
                            {"type": "TextBlock", "color": "Light", "isSubtle": True,
                             "text": f"{critical} Críticas · {high} Altas · {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
                        ]
                    },
                    *facts
                ],
                "actions": [{
                    "type": "Action.OpenUrl",
                    "title": "Ver en NVD",
                    "url": "https://nvd.nist.gov/vuln/search"
                }]
            }
        }]
    }

    requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=15)

@app.post("/inventario")
def recibir_inventario(data: dict):
    """Recibe dependencias, guarda en MongoDB y comprueba CVEs"""
    data["fecha"] = datetime.now().isoformat()
    inventario.replace_one({"repo": data["repo"]}, data, upsert=True)

    # Comprobar CVEs para cada dependencia
    alerts = []
    for dep in data.get("dependencias", []):
        name = dep.get("name", "")
        version = dep.get("version", "")
        print(f"  Checking: {name} {version}...")

        vulns = query_nvd(name)
        for v in vulns:
            severity, score = parse_severity(v)
            if severity not in NOTIFY_SEVERITIES:
                continue
            cve = v.get("cve", {})
            alerts.append({
                "repo": data["repo"],
                "name": name,
                "version": version,
                "cve_id": cve.get("id", "UNKNOWN"),
                "severity": severity,
                "score": score,
            })

        time.sleep(1)

    if alerts:
        alerts.sort(key=lambda x: x["score"], reverse=True)
        send_to_teams(alerts)
        print(f"[INFO] {len(alerts)} alertas enviadas a Teams")

    return {"status": "ok", "repo": data["repo"], "alertas": len(alerts)}

@app.get("/inventario")
def get_inventario():
    """Devuelve todo el inventario"""
    return list(inventario.find({}, {"_id": 0}))

@app.get("/inventario/{repo}")
def get_repo(repo: str):
    """Devuelve las dependencias de un repositorio concreto"""
    result = inventario.find_one({"repo": repo}, {"_id": 0})
    if not result:
        return {"error": "Repositorio no encontrado"}
    return result
