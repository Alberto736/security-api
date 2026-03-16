from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime
import os

app = FastAPI()

# Conexión a MongoDB
MONGO_URL = os.environ.get("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["security"]
inventario = db["inventario"]

@app.post("/inventario")
def recibir_inventario(data: dict):
    """Recibe dependencias de un repositorio y las guarda en MongoDB"""
    data["fecha"] = datetime.now().isoformat()
    inventario.replace_one(
        {"repo": data["repo"]},
        data,
        upsert=True
    )
    return {"status": "ok", "repo": data["repo"]}

@app.get("/inventario")
def get_inventario():
    """Devuelve todo el inventario"""
    repos = list(inventario.find({}, {"_id": 0}))
    return repos

@app.get("/inventario/{repo}")
def get_repo(repo: str):
    """Devuelve las dependencias de un repositorio concreto"""
    result = inventario.find_one({"repo": repo}, {"_id": 0})
    if not result:
        return {"error": "Repositorio no encontrado"}
    return result
