import asyncio
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from app.schemas import Alert, InventoryIn, InventoryPostResponse
from app.services.nvd import query_nvd
from app.services.osv import query_osv
from app.settings import Settings, get_settings
from app.security import require_api_key

router = APIRouter(
    prefix="/inventario",
    tags=["inventario"],
    dependencies=[Depends(require_api_key)],
)


def _inventory_collection(settings: Settings, request: Request):
    mongo = getattr(request.app.state, "mongo", None)
    if mongo is None:
        raise RuntimeError("Mongo not configured in app state")
    return mongo.db[settings.mongo_inventory_collection]


@router.post("", response_model=InventoryPostResponse, status_code=201)
async def recibir_inventario(
    data: InventoryIn,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> InventoryPostResponse:
    now = datetime.now(timezone.utc)
    stored = data.model_dump()
    stored["fecha"] = now.isoformat()

    col = _inventory_collection(settings, request)
    await col.replace_one({"repo": data.repo}, stored, upsert=True)

    alerts: list[Alert] = []
    seen: set[str] = set()

    timeout = httpx.Timeout(settings.request_timeout_seconds)
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        for dep in data.dependencias:
            name = dep.name
            version = dep.version
            ecosystem = dep.ecosystem

            # NVD
            for finding in await query_nvd(settings, client, name, version):
                if finding.severity not in {"CRITICAL", "HIGH"}:
                    continue
                if finding.cve_id in seen:
                    continue
                alerts.append(
                    Alert(
                        repo=data.repo,
                        name=name,
                        version=version,
                        cve_id=finding.cve_id,
                        severity=finding.severity,
                        score=finding.score,
                        source="NVD",
                    )
                )
                seen.add(finding.cve_id)

            # OSV
            for finding in await query_osv(client, name=name, version=version, ecosystem=ecosystem):
                if finding.cve_id in seen:
                    continue
                alerts.append(
                    Alert(
                        repo=data.repo,
                        name=name,
                        version=version,
                        cve_id=finding.cve_id,
                        severity="HIGH",
                        score=7.5,
                        source="OSV",
                    )
                )
                seen.add(finding.cve_id)

            await asyncio.sleep(settings.request_delay_seconds)

    alerts.sort(key=lambda a: a.score, reverse=True)
    return InventoryPostResponse(
        repo=data.repo,
        alertas_encontradas=len(alerts),
        detalle=alerts,
    )


@router.get("")
async def get_inventario(request: Request, settings: Settings = Depends(get_settings)):
    col = _inventory_collection(settings, request)
    docs = await col.find({}, {"_id": 0}).to_list(length=1000)
    return docs


@router.get("/{repo}")
async def get_repo(repo: str, request: Request, settings: Settings = Depends(get_settings)):
    col = _inventory_collection(settings, request)
    doc = await col.find_one({"repo": repo}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Repositorio no encontrado")
    return doc

