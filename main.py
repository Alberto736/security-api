import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import Mongo, mongo_lifespan
from app.routers.health import router as health_router
from app.routers.inventario import router as inventario_router
from app.settings import get_settings


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_logging()

    # Create settings + Mongo lazily so importing doesn't require env vars.
    settings = get_settings()
    mongo = Mongo(settings)
    app.state.mongo = mongo

    async with mongo_lifespan(mongo):
        yield


app = FastAPI(
    title="security-api",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(inventario_router)
