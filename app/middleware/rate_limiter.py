"""Rate limiting middleware for API protection."""
import time
from collections import defaultdict
from typing import Dict, Tuple

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, HTTPException, status

from app.logging_config import get_logger, log_security_event


def get_client_identifier(request: Request) -> str:
    """Get client identifier for rate limiting."""
    # Try to get API key first (more specific)
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key[:8]}"  # Use first 8 chars for privacy
    
    # Fall back to IP address
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return f"ip:{forwarded_for.split(',')[0].strip()}"
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return f"ip:{real_ip.strip()}"
    
    return f"ip:{get_remote_address(request)}"


# Create limiter instance
limiter = Limiter(key_func=get_client_identifier)


class InMemoryRateLimiter:
    """Simple in-memory rate limiter for demonstration."""
    
    def __init__(self):
        self.requests: Dict[str, list[float]] = defaultdict(list)
        self.logger = get_logger("rate_limiter")
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window: int = 60
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Client identifier
            limit: Number of requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        now = time.time()
        window_start = now - window
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        # Check if under limit
        current_count = len(self.requests[key])
        is_allowed = current_count < limit
        
        if is_allowed:
            # Add current request
            self.requests[key].append(now)
        else:
            # Log rate limit exceeded
            self.logger.warning(
                "Rate limit exceeded",
                client_key=key,
                current_requests=current_count,
                limit=limit,
                window_seconds=window
            )
        
        # Return rate limit info
        return is_allowed, {
            "limit": limit,
            "remaining": max(0, limit - current_count - (1 if not is_allowed else 0)),
            "reset_time": int(window_start + window + window)
        }
    
    def reset(self, key: str) -> None:
        """Reset rate limit for a specific client."""
        if key in self.requests:
            del self.requests[key]


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded) -> HTTPException:
    """Handle rate limit exceeded exceptions."""
    logger = get_logger("security")
    
    # Log security event
    logger.warning(
        "Rate limit exceeded",
        **log_security_event(
            event_type="rate_limit_exceeded",
            severity="medium",
            client_ip=get_client_identifier(request),
            path=request.url.path,
            method=request.method
        )
    )
    
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "message": str(exc),
            "retry_after": 60  # Suggest retry after 1 minute
        }
    )
