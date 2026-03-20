"""Request logging middleware for structured logging."""
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import get_logger, log_request_info


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses with structured data."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Store request ID in state for use in endpoints
        request.state.request_id = request_id
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Start timing
        start_time = time.time()
        
        # Log request
        logger = get_logger("request")
        logger.info(
            "Request started",
            **log_request_info(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                query_params=str(request.query_params),
                client_ip=client_ip,
                user_agent=request.headers.get("user-agent", "unknown")
            )
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                **log_request_info(
                    request_id=request_id,
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=round(duration * 1000, 2),
                    client_ip=client_ip
                )
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            # Calculate duration for failed request
            duration = time.time() - start_time
            
            # Log error
            logger.error(
                "Request failed",
                **log_request_info(
                    request_id=request_id,
                    method=request.method,
                    path=request.url.path,
                    duration_ms=round(duration * 1000, 2),
                    client_ip=client_ip,
                    error_type=type(exc).__name__,
                    error_message=str(exc)
                )
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, considering proxies."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the list
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to client IP
        return request.client.host if request.client else "unknown"
