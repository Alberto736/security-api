"""Error handling middleware and exception handlers."""
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException

from app.logging_config import get_logger, log_security_event


class SecurityAPIException(Exception):
    """Base exception for Security API."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(SecurityAPIException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            details=details
        )


class SecurityException(SecurityAPIException):
    """Exception for security-related errors."""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="SECURITY_ERROR",
            details=details
        )


class RateLimitException(SecurityAPIException):
    """Exception for rate limiting."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


async def security_api_exception_handler(request: Request, exc: SecurityAPIException) -> JSONResponse:
    """Handle custom Security API exceptions."""
    logger = get_logger("error_handler")
    
    # Log the error
    logger.error(
        "Security API exception",
        error_code=exc.error_code,
        status_code=exc.status_code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
        method=request.method,
        request_id=getattr(request.state, "request_id", "unknown")
    )
    
    # Return structured error response
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "request_id": getattr(request.state, "request_id", "unknown")
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI validation errors."""
    logger = get_logger("error_handler")
    
    # Extract validation errors
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    # Log validation error
    logger.warning(
        "Validation error",
        errors=errors,
        path=request.url.path,
        method=request.method,
        request_id=getattr(request.state, "request_id", "unknown")
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": {"validation_errors": errors},
                "request_id": getattr(request.state, "request_id", "unknown")
            }
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger = get_logger("error_handler")
    
    # Log HTTP exception
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
        request_id=getattr(request.state, "request_id", "unknown")
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "request_id": getattr(request.state, "request_id", "unknown")
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger = get_logger("error_handler")
    
    # Log unexpected error
    logger.error(
        "Unexpected error",
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        method=request.method,
        request_id=getattr(request.state, "request_id", "unknown")
    )
    
    # Don't expose internal error details in production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
                "request_id": getattr(request.state, "request_id", "unknown")
            }
        }
    )


def add_error_handlers(app: FastAPI) -> None:
    """Add all exception handlers to the FastAPI app."""
    app.add_exception_handler(SecurityAPIException, security_api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
