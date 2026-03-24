from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Request, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas import HealthResponse
from app.settings import Settings, get_settings
from app.logging_config import get_logger

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


async def check_database(settings: Settings, request: Request) -> Dict[str, Any]:
    """Check database connectivity."""
    try:
        mongo = getattr(request.app.state, "mongo", None)
        if mongo is None:
            return {
                "status": "error",
                "message": "MongoDB not configured"
            }
        
        # Test database connection
        db: AsyncIOMotorDatabase = mongo.db
        await db.command("ping")
        
        # Check collection exists and is accessible
        collection = db[settings.mongo_inventory_collection]
        await collection.count_documents({}, limit=1)
        
        return {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger = get_logger("health")
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }


async def check_external_services() -> Dict[str, Any]:
    """Check external API services status."""
    results = {}
    
    # Check NVD API
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("https://services.nvd.nist.gov/rest/json/cves/2.0")
            if response.status_code == 200:
                results["nvd_api"] = {
                    "status": "healthy",
                    "status_code": response.status_code
                }
            else:
                results["nvd_api"] = {
                    "status": "degraded",
                    "status_code": response.status_code,
                    "message": f"Unexpected status code: {response.status_code}"
                }
    except Exception as e:
        results["nvd_api"] = {
            "status": "degraded",
            "message": str(e)
        }
    
    # Check OSV API
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "https://api.osv.dev/v1/query",
                json={"package": {"name": "test", "ecosystem": "npm"}}
            )
            if response.status_code in [200, 400]:  # 400 is ok for test query
                results["osv_api"] = {
                    "status": "healthy",
                    "status_code": response.status_code
                }
            else:
                results["osv_api"] = {
                    "status": "degraded",
                    "status_code": response.status_code,
                    "message": f"Unexpected status code: {response.status_code}"
                }
    except Exception as e:
        results["osv_api"] = {
            "status": "degraded",
            "message": str(e)
        }
    
    return results


async def check_memory_usage() -> Dict[str, Any]:
    """Check memory usage."""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "status": "healthy",
            "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
            "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
            "percent": round(process.memory_percent(), 2)
        }
    except ImportError:
        return {
            "status": "unknown",
            "message": "psutil not available"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("", response_model=HealthResponse)
async def health_check(
    request: Request,
    settings: Settings = Depends(get_settings)
) -> HealthResponse:
    """
    Comprehensive health check endpoint.
    
    Returns:
        Health status with detailed component checks
    """
    logger = get_logger("health")
    
    checks = {}
    overall_status = "ok"
    
    # Database check
    db_check = await check_database(settings, request)
    checks["database"] = db_check
    if db_check["status"] != "healthy":
        overall_status = "error"
    
    # External APIs check
    api_checks = await check_external_services()
    checks["external_apis"] = api_checks
    if any(check["status"] == "error" for check in api_checks.values()):
        overall_status = "error"
    elif any(check["status"] == "degraded" for check in api_checks.values()) and overall_status == "ok":
        overall_status = "degraded"
    
    # Memory check
    memory_check = await check_memory_usage()
    checks["memory"] = memory_check
    if memory_check["status"] == "error":
        overall_status = "error"
    
    # Security configuration check
    checks["security"] = {
        "status": "healthy",
        "api_key_required": settings.api_key_required,
        "rate_limit_enabled": settings.rate_limit_enabled,
        "cors_configured": len(settings.cors_origins) > 0
    }
    
    # Log health check
    logger.info(
        "Health check performed",
        overall_status=overall_status,
        checks_count=len(checks)
    )
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        version="0.1.0",
        environment=settings.environment,
        checks=checks
    )


@router.get("/simple")
async def simple_health_check() -> dict[str, str]:
    """
    Simple health check for load balancers.
    
    Returns:
        Simple status response
    """
    return {"status": "ok"}
