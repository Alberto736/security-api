"""Simple rate limiting middleware for enterprise use."""
import time
from collections import defaultdict
from typing import Dict

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.logging_config import get_logger


class SimpleRateLimiter(BaseHTTPMiddleware):
    """Simple in-memory rate limiter for basic protection."""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list[float]] = defaultdict(list)
        self.logger = get_logger("rate_limiter")
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if not self._is_allowed(client_ip):
            self.logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                path=request.url.path
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        return request.client.host if request.client else "unknown"
    
    def _is_allowed(self, client_ip: str) -> bool:
        """Check if client is allowed to make request."""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        # Check if under limit
        return len(self.requests[client_ip]) < self.requests_per_minute
