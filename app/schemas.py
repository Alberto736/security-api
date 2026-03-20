from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, validator, HttpUrl
import re


Ecosystem = Literal["npm", "pip", "maven", "gradle", "composer", "nuget", "rubygems", "cargo", "golang", "docker"]


class DependencyItem(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Package name")
    version: str | None = Field(default=None, max_length=50, description="Package version")
    ecosystem: Ecosystem = Field(default="npm", description="Package ecosystem")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate package name for security."""
        if not v or not v.strip():
            raise ValueError("Package name cannot be empty")
        
        # Remove potential injection attempts
        v = v.strip()
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'[<>]',  # HTML tags
            r'[;&|`$]',  # Command injection
            r'\.\./',  # Path traversal
            r'javascript:',  # XSS
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Invalid characters in package name: {v}")
        
        return v
    
    @validator('version')
    def validate_version(cls, v):
        """Validate package version for security."""
        if v is None:
            return v
        
        v = v.strip()
        
        # Basic semantic version pattern
        if not re.match(r'^[\w\.\-+]+$', v):
            raise ValueError(f"Invalid version format: {v}")
        
        return v


class InventoryIn(BaseModel):
    repo: str = Field(min_length=1, max_length=255, description="Repository identifier")
    dependencias: list[DependencyItem] = Field(default_factory=list, max_items=1000, description="List of dependencies")
    
    @validator('repo')
    def validate_repo(cls, v):
        """Validate repository name for security."""
        if not v or not v.strip():
            raise ValueError("Repository name cannot be empty")
        
        v = v.strip()
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'[<>]',  # HTML tags
            r'[;&|`$]',  # Command injection
            r'\.\./',  # Path traversal
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Invalid characters in repository name: {v}")
        
        return v
    
    @validator('dependencias')
    def validate_dependencies(cls, v):
        """Validate dependencies list."""
        if len(v) > 1000:
            raise ValueError("Too many dependencies (max 1000)")
        
        return v


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
    alertas_encontradas: int = Field(ge=0, description="Number of alerts found")
    detalle: list[Alert] = Field(description="Detailed alert information")


class HealthResponse(BaseModel):
    status: Literal["ok", "error"] = "ok"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="0.1.0")
    environment: str = Field(default="development")
    checks: dict[str, dict] = Field(default_factory=dict)


class SecurityConfig(BaseModel):
    """Security configuration model."""
    max_request_size: int = Field(default=10 * 1024 * 1024, ge=1024, le=100 * 1024 * 1024)
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=100, ge=1, le=10000)
    rate_limit_window: int = Field(default=60, ge=1, le=3600)
