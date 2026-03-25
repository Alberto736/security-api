"""
Unit tests for Pydantic schemas and validation.
"""
import pytest
from pydantic import ValidationError

from app.schemas import (
    DependencyItem,
    InventoryIn,
    Alert,
    InventoryPostResponse,
    HealthResponse,
    SecurityConfig
)


class TestDependencyItem:
    """Test DependencyItem schema validation."""
    
    @pytest.mark.unit
    def test_valid_dependency_item(self):
        """Test creating a valid dependency item."""
        dep = DependencyItem(
            name="requests",
            version="2.32.0",
            ecosystem="pip"
        )
        assert dep.name == "requests"
        assert dep.version == "2.32.0"
        assert dep.ecosystem == "pip"
    
    @pytest.mark.unit
    def test_dependency_item_default_values(self):
        """Test dependency item with default values."""
        dep = DependencyItem(name="react")
        assert dep.name == "react"
        assert dep.version is None
        assert dep.ecosystem == "npm"
    
    @pytest.mark.unit
    def test_dependency_item_invalid_name_empty(self):
        """Test dependency item with empty name."""
        with pytest.raises(ValidationError) as exc_info:
            DependencyItem(name="")
        
        errors = exc_info.value.errors()
        assert any("String should have at least 1 character" in str(error) for error in errors)
    
    @pytest.mark.unit
    def test_dependency_item_invalid_name_injection(self):
        """Test dependency item with injection attempts."""
        invalid_names = [
            "<script>alert('xss')</script>",
            "package; rm -rf /",
            "package`whoami`",
            "package|cat /etc/passwd",
            "../../../etc/passwd",
            "javascript:alert('xss')"
        ]
        
        for invalid_name in invalid_names:
            with pytest.raises(ValidationError) as exc_info:
                DependencyItem(name=invalid_name)
            
            errors = exc_info.value.errors()
            assert any("Invalid characters" in str(error) for error in errors)
    
    @pytest.mark.unit
    def test_dependency_item_invalid_version(self):
        """Test dependency item with invalid version."""
        with pytest.raises(ValidationError) as exc_info:
            DependencyItem(name="test", version="invalid@version#")
        
        errors = exc_info.value.errors()
        assert any("Invalid version format" in str(error) for error in errors)
    
    @pytest.mark.unit
    def test_dependency_item_valid_version_formats(self):
        """Test various valid version formats."""
        valid_versions = [
            "1.0.0",
            "2.1.3-alpha",
            "3.0.0-beta.1",
            "1.2.3+build.123",
            "latest",
            "v1.2.3",
            "1.0.0-rc.1+build.123"
        ]
        
        for version in valid_versions:
            dep = DependencyItem(name="test", version=version)
            assert dep.version == version
    
    @pytest.mark.unit
    def test_dependency_item_name_length_limits(self):
        """Test name length validation."""
        # Test minimum length
        with pytest.raises(ValidationError):
            DependencyItem(name="")
        
        # Test maximum length
        long_name = "a" * 256
        with pytest.raises(ValidationError):
            DependencyItem(name=long_name)
        
        # Test valid length
        valid_name = "a" * 255
        dep = DependencyItem(name=valid_name)
        assert dep.name == valid_name


class TestInventoryIn:
    """Test InventoryIn schema validation."""
    
    @pytest.mark.unit
    def test_valid_inventory(self):
        """Test creating a valid inventory."""
        inventory = InventoryIn(
            repo="test-repo",
            dependencias=[
                DependencyItem(name="requests", version="2.32.0", ecosystem="pip"),
                DependencyItem(name="react", version="18.2.0", ecosystem="npm")
            ]
        )
        assert inventory.repo == "test-repo"
        assert len(inventory.dependencias) == 2
    
    @pytest.mark.unit
    def test_inventory_empty_dependencies(self):
        """Test inventory with no dependencies."""
        inventory = InventoryIn(repo="test-repo")
        assert inventory.repo == "test-repo"
        assert len(inventory.dependencias) == 0
    
    @pytest.mark.unit
    def test_inventory_invalid_repo(self):
        """Test inventory with invalid repo name."""
        with pytest.raises(ValidationError) as exc_info:
            InventoryIn(repo="<script>alert('xss')</script>")
        
        errors = exc_info.value.errors()
        assert any("Invalid characters" in str(error) for error in errors)
    
    @pytest.mark.unit
    def test_inventory_too_many_dependencies(self):
        """Test inventory with too many dependencies."""
        dependencies = [DependencyItem(name=f"pkg{i}") for i in range(1001)]
        
        with pytest.raises(ValidationError) as exc_info:
            InventoryIn(repo="test", dependencias=dependencies)
        
        errors = exc_info.value.errors()
        assert any("List should have at most 1000 items" in str(error) for error in errors)


class TestAlert:
    """Test Alert schema validation."""
    
    @pytest.mark.unit
    def test_valid_alert(self):
        """Test creating a valid alert."""
        alert = Alert(
            repo="test-repo",
            name="requests",
            version="2.32.0",
            cve_id="CVE-2023-1234",
            severity="HIGH",
            score=8.5,
            source="NVD"
        )
        assert alert.repo == "test-repo"
        assert alert.cve_id == "CVE-2023-1234"
        assert alert.severity == "HIGH"
        assert alert.score == 8.5
        assert alert.source == "NVD"
    
    @pytest.mark.unit
    def test_alert_optional_version(self):
        """Test alert without version."""
        alert = Alert(
            repo="test-repo",
            name="requests",
            cve_id="CVE-2023-1234",
            severity="HIGH",
            score=8.5,
            source="NVD"
        )
        assert alert.version is None


class TestInventoryPostResponse:
    """Test InventoryPostResponse schema validation."""
    
    @pytest.mark.unit
    def test_valid_response(self):
        """Test creating a valid response."""
        response = InventoryPostResponse(
            repo="test-repo",
            alertas_encontradas=5,
            detalle=[
                Alert(
                    repo="test-repo",
                    name="requests",
                    cve_id="CVE-2023-1234",
                    severity="HIGH",
                    score=8.5,
                    source="NVD"
                )
            ]
        )
        assert response.status == "ok"
        assert response.repo == "test-repo"
        assert response.alertas_encontradas == 5
        assert len(response.detalle) == 1
    
    @pytest.mark.unit
    def test_response_negative_alerts(self):
        """Test response with negative alert count."""
        with pytest.raises(ValidationError):
            InventoryPostResponse(
                repo="test-repo",
                alertas_encontradas=-1,
                detalle=[]
            )


class TestHealthResponse:
    """Test HealthResponse schema validation."""
    
    @pytest.mark.unit
    def test_valid_health_response(self):
        """Test creating a valid health response."""
        response = HealthResponse(
            status="ok",
            checks={
                "database": {"status": "healthy"},
                "external_apis": {"nvd_api": {"status": "healthy"}}
            }
        )
        assert response.status == "ok"
        assert "database" in response.checks
        assert response.environment == "development"
        assert response.version == "0.1.0"
    
    @pytest.mark.unit
    def test_health_response_error_status(self):
        """Test health response with error status."""
        response = HealthResponse(status="error")
        assert response.status == "error"


class TestSecurityConfig:
    """Test SecurityConfig schema validation."""
    
    @pytest.mark.unit
    def test_valid_security_config(self):
        """Test creating a valid security config."""
        config = SecurityConfig(
            max_request_size=5 * 1024 * 1024,
            rate_limit_enabled=True,
            rate_limit_requests=50,
            rate_limit_window=30
        )
        assert config.max_request_size == 5 * 1024 * 1024
        assert config.rate_limit_enabled is True
        assert config.rate_limit_requests == 50
        assert config.rate_limit_window == 30
    
    @pytest.mark.unit
    def test_security_config_default_values(self):
        """Test security config with default values."""
        config = SecurityConfig()
        assert config.max_request_size == 10 * 1024 * 1024
        assert config.rate_limit_enabled is True
        assert config.rate_limit_requests == 100
        assert config.rate_limit_window == 60
    
    @pytest.mark.unit
    def test_security_config_validation_limits(self):
        """Test security config validation limits."""
        # Test minimum values
        config = SecurityConfig(
            max_request_size=1024,
            rate_limit_requests=1,
            rate_limit_window=1
        )
        assert config.max_request_size == 1024
        assert config.rate_limit_requests == 1
        assert config.rate_limit_window == 1
        
        # Test maximum values
        config = SecurityConfig(
            max_request_size=100 * 1024 * 1024,
            rate_limit_requests=10000,
            rate_limit_window=3600
        )
        assert config.max_request_size == 100 * 1024 * 1024
        assert config.rate_limit_requests == 10000
        assert config.rate_limit_window == 3600
    
    @pytest.mark.unit
    def test_security_config_invalid_values(self):
        """Test security config with invalid values."""
        # Test request size too small
        with pytest.raises(ValidationError):
            SecurityConfig(max_request_size=512)
        
        # Test request size too large
        with pytest.raises(ValidationError):
            SecurityConfig(max_request_size=200 * 1024 * 1024)
        
        # Test rate limit requests out of range
        with pytest.raises(ValidationError):
            SecurityConfig(rate_limit_requests=0)
        
        with pytest.raises(ValidationError):
            SecurityConfig(rate_limit_requests=20000)
        
        # Test rate limit window out of range
        with pytest.raises(ValidationError):
            SecurityConfig(rate_limit_window=0)
        
        with pytest.raises(ValidationError):
            SecurityConfig(rate_limit_window=7200)
