from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from datetime import datetime
import os
import time
import requests

app = FastAPI()

# 1. Configuración de MongoDB con validación
MONGO_URL = os.environ.get("MONGO_URI")
if not MONGO_URL:
    # Si no hay URI, usamos una por defecto para evitar que el cliente de mongo falle
    MONGO_URL = "mongodb://user:password@mongo:27017/hermod?authSource=hermod"

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NOTIFY_SEVERITIES = {"CRITICAL", "HIGH"}

# Conexión
client = MongoClient(MONGO_URL)
db = client["hermod"]
inventario_col = db["inventario"]

def query_nvd(keyword):
    params = {"keywordSearch": keyword, "resultsPerPage": 50}
    try:
        # Añadimos un User-Agent para evitar bloqueos de la API de NVD
        headers = {"User-Agent": "HermodSecurityAPI/1.0"}
        response = requests.get(NVD_API_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("vulnerabilities", [])
    except Exception as e:
        print(f"[Error NVD] {e}")
        return []

def query_osv(name, version, ecosystem):
    ecosystem_map = {
        "npm": "npm", "pip": "PyPI", "maven": "Maven", "gradle": "Maven",
        "composer": "Packagist", "nuget": "NuGet", "rubygems": "RubyGems",
        "cargo": "crates.io", "golang": "Go", "docker": "Docker",
    }
    osv_ecosystem = ecosystem_map.get(ecosystem.lower(), "")
    if not osv_ecosystem:
        return []
    
    payload = {
        "version": version,
        "package": {"name": name, "ecosystem": osv_ecosystem}
    }
    try:
        response = requests.post("https://api.osv.dev/v1/query", json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("vulns", [])
    except Exception as e:
        print(f"[Error OSV] {e}")
        return []

def parse_severity(vuln):
    metrics = vuln.get("cve", {}).get("metrics", {})
    # Prioridad: v3.1 > v3.0 > v2
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if key in metrics and metrics[key]:
            data = metrics[key][0].get("cvssData", {})
            # NVD usa 'baseSeverity' para V3 y 'severity' para V2
            severity = data.get("baseSeverity") or metrics[key][0].get("baseSeverity") or "UNKNOWN"
            return severity.upper(), data.get("baseScore", 0.0)
    return "UNKNOWN", 0.0

@app.post("/inventario")
def recibir_inventario(data: dict):
    # Validación básica para evitar el Error 500
    repo_name = data.get("repo")
    if not repo_name:
        raise HTTPException(status_code=400, detail="El campo 'repo' es obligatorio")

    data["fecha"] = datetime.now().isoformat()
    
    # Guardar en Mongo (usamos la variable inventario_col para no confundir con el endpoint)
    inventario_col.replace_one({"repo": repo_name}, data, upsert=True)

    alerts = []
    seen_cves = set() # Para evitar duplicados rápido

    for dep in data.get("dependencias", []):
        name = dep.get("name", "")
        version = dep.get("version", "")
        ecosystem = dep.get("ecosystem", "npm") # default a npm
        
        if not name: continue
        print(f"Checking: {name} {version}...")

        # 1. Consulta NVD
        vulns_nvd = query_nvd(name)
        for v in vulns_nvd:
            severity, score = parse_severity(v)
            if severity in NOTIFY_SEVERITIES:
                cve_id = v.get("cve", {}).get("id", "UNKNOWN")
                if cve_id not in seen_cves:
                    alerts.append({
                        "repo": repo_name,
                        "name": name,
                        "version": version,
                        "cve_id": cve_id,
                        "severity": severity,
                        "score": score,
                        "source": "NVD"
                    })
                    seen_cves.add(cve_id)

        # 2. Consulta OSV
        vulns_osv = query_osv(name, version, ecosystem)
        for v in vulns_osv:
            osv_id = v.get("id", "UNKNOWN")
            aliases = v.get("aliases", [])
            cve_id = next((a for a in aliases if a.startswith("CVE-")), osv_id)
            
            if cve_id not in seen_cves:
                alerts.append({
                    "repo": repo_name,
                    "name": name,
                    "version": version,
                    "cve_id": cve_id,
                    "severity": "HIGH", # OSV a veces no da severity simple
                    "score": 7.5,
                    "source": "OSV"
                })
                seen_cves.add(cve_id)

        # Pequeño respiro para no saturar APIs
        time.sleep(0.5)

    if alerts:
        alerts.sort(key=lambda x: x["score"], reverse=True)
        print(f"[INFO] {len(alerts)} alertas encontradas para {repo_name}")

    return {"status": "ok", "repo": repo_name, "alertas_encontradas": len(alerts), "detalle": alerts}

@app.get("/inventario")
def get_inventario():
    return list(inventario_col.find({}, {"_id": 0}))

@app.get("/inventario/{repo}")
def get_repo(repo: str):
    result = inventario_col.find_one({"repo": repo}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")
    return result
