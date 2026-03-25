import logging
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.db import Mongo, mongo_lifespan
from app.routers.health import router as health_router
from app.routers.inventario import router as inventario_router
from app.settings import get_settings
from app.logging_config import setup_logging, get_logger
from app.middleware.error_handler import add_error_handlers
from app.middleware.request_logging import RequestLoggingMiddleware

# Get settings at module level for middleware
settings = get_settings()


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create settings + Mongo lazily so importing doesn't require env vars.
    mongo = Mongo(settings)
    app.state.mongo = mongo
    app.state.settings = settings

    # Setup structured logging
    setup_logging(
        log_level=settings.log_level,
        json_logs=settings.json_logs
    )
    logger = get_logger(__name__)
    logger.info("Starting security-api", version="0.1.0")

    async with mongo_lifespan(mongo):
        logger.info("Application ready")
        yield
        logger.info("Shutting down application")


app = FastAPI(
    title="security-api",
    version="0.1.0",
    lifespan=lifespan,
    description="API for security vulnerability scanning and inventory management",
)

# Add CORS middleware (configure properly for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add error handlers
add_error_handlers(app)

app.include_router(health_router)
app.include_router(inventario_router)
