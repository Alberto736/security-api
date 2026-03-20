from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Ecosystem = Literal["npm", "pip", "maven", "gradle", "composer", "nuget", "rubygems", "cargo", "golang", "docker"]


class DependencyItem(BaseModel):
    name: str = Field(min_length=1)
    version: str | None = None
    ecosystem: Ecosystem = "npm"


class InventoryIn(BaseModel):
    repo: str = Field(min_length=1)
    dependencias: list[DependencyItem] = Field(default_factory=list)


class Alert(BaseModel):
    repo: str
    name: str
    version: str | None = None
    cve_id: str
    severity: str
    score: float
    source: Literal["NVD", "OSV"]


class InventoryStored(InventoryIn):
    fecha: datetime


class InventoryPostResponse(BaseModel):
    status: Literal["ok"] = "ok"
    repo: str
    alertas_encontradas: int
    detalle: list[Alert]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
