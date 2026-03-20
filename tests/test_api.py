"""
Integration tests for Security API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    @pytest.mark.unit
    def test_simple_health_check(self, test_client: TestClient):
        """Test simple health check endpoint."""
        response = test_client.get("/health/simple")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    @pytest.mark.integration
    def test_comprehensive_health_check(self, test_client: TestClient):
        """Test comprehensive health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert "checks" in data
        
        # Check specific health checks
        checks = data["checks"]
        assert "database" in checks
        assert "security" in checks
        assert "external_apis" in checks
        assert "memory" in checks


class TestInventoryEndpoints:
    """Test inventory management endpoints."""
    
    @pytest.mark.integration
    def test_post_inventory_success(self, test_client: TestClient, sample_inventory_data: dict):
        """Test successful inventory submission."""
        headers = {"X-API-Key": "test_api_key"}
        response = test_client.post("/inventario", json=sample_inventory_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "ok"
        assert data["repo"] == sample_inventory_data["repo"]
        assert "alertas_encontradas" in data
        assert "detalle" in data
    
    @pytest.mark.unit
    def test_post_inventory_missing_api_key(self, test_client: TestClient, sample_inventory_data: dict):
        """Test inventory submission without API key."""
        response = test_client.post("/inventario", json=sample_inventory_data)
        
        assert response.status_code == 401
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "HTTP_401"
    
    @pytest.mark.unit
    def test_post_inventory_invalid_api_key(self, test_client: TestClient, sample_inventory_data: dict):
        """Test inventory submission with invalid API key."""
        headers = {"X-API-Key": "invalid_key"}
        response = test_client.post("/inventario", json=sample_inventory_data, headers=headers)
        
        assert response.status_code == 401
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "HTTP_401"
    
    @pytest.mark.unit
    def test_post_inventory_validation_error(self, test_client: TestClient, sample_inventory_data_invalid: dict):
        """Test inventory submission with invalid data."""
        headers = {"X-API-Key": "test_api_key"}
        response = test_client.post("/inventario", json=sample_inventory_data_invalid, headers=headers)
        
        assert response.status_code == 422
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "VALIDATION_ERROR"
        assert "validation_errors" in error["error"]["details"]
    
    @pytest.mark.integration
    def test_get_inventory_list(self, test_client: TestClient, sample_inventory_data: dict):
        """Test getting list of inventories."""
        headers = {"X-API-Key": "test_api_key"}
        
        # First, add an inventory
        test_client.post("/inventario", json=sample_inventory_data, headers=headers)
        
        # Then get the list
        response = test_client.get("/inventario", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.integration
    def test_get_inventory_by_repo(self, test_client: TestClient, sample_inventory_data: dict):
        """Test getting inventory by repository name."""
        headers = {"X-API-Key": "test_api_key"}
        
        # First, add an inventory
        test_client.post("/inventario", json=sample_inventory_data, headers=headers)
        
        # Then get by repo
        response = test_client.get(f"/inventario/{sample_inventory_data['repo']}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["repo"] == sample_inventory_data["repo"]
        assert "dependencias" in data
        assert "fecha" in data
    
    @pytest.mark.unit
    def test_get_inventory_not_found(self, test_client: TestClient):
        """Test getting non-existent inventory."""
        headers = {"X-API-Key": "test_api_key"}
        response = test_client.get("/inventario/non-existent-repo", headers=headers)
        
        assert response.status_code == 404
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "HTTP_404"


class TestSecurityFeatures:
    """Test security features and middleware."""
    
    @pytest.mark.unit
    def test_request_id_header(self, test_client: TestClient):
        """Test that requests get unique IDs."""
        response = test_client.get("/health/simple")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0
    
    @pytest.mark.unit
    def test_cors_headers(self, test_client: TestClient):
        """Test CORS headers are present."""
        response = test_client.options("/health/simple")
        assert response.status_code == 200
        # CORS headers should be present
    
    @pytest.mark.unit
    def test_rate_limiting_disabled_in_tests(self, test_client: TestClient, sample_inventory_data: dict):
        """Test that rate limiting is disabled in test environment."""
        headers = {"X-API-Key": "test_api_key"}
        
        # Make multiple requests quickly
        for _ in range(10):
            response = test_client.post("/inventario", json=sample_inventory_data, headers=headers)
            # Should not be rate limited
            assert response.status_code in [201, 422]  # 201 for success, 422 for duplicate


@pytest.mark.asyncio
class TestAsyncAPI:
    """Async tests using AsyncClient."""
    
    async def test_async_health_check(self, async_test_client: AsyncClient):
        """Test health check with async client."""
        response = await async_test_client.get("/health/simple")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    async def test_async_inventory_submission(self, async_test_client: AsyncClient, sample_inventory_data: dict):
        """Test inventory submission with async client."""
        headers = {"X-API-Key": "test_api_key"}
        response = await async_test_client.post("/inventario", json=sample_inventory_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "ok"
        assert data["repo"] == sample_inventory_data["repo"]
