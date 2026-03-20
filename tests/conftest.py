"""
Pytest configuration and fixtures for Security API tests.
"""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from main import app
from app.settings import Settings, get_settings
from app.db import Mongo


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Test settings with in-memory database."""
    return Settings(
        mongo_uri="mongodb://localhost:27017/test_security_api",
        mongo_db="test_security_api",
        mongo_inventory_collection="test_inventario",
        api_key="test_api_key",
        api_key_required=True,
        rate_limit_enabled=False,  # Disable rate limiting for tests
        log_level="DEBUG",
        json_logs=False,
        environment="testing"
    )


@pytest.fixture
def test_client(test_settings: Settings) -> TestClient:
    """Create a test client with overridden settings."""
    def override_get_settings():
        return test_settings
    
    app.dependency_overrides[get_settings] = override_get_settings
    
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_test_client(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with overridden settings."""
    def override_get_settings():
        return test_settings
    
    app.dependency_overrides[get_settings] = override_get_settings
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_mongo(test_settings: Settings) -> AsyncGenerator[Mongo, None]:
    """Create a test MongoDB connection."""
    mongo = Mongo(test_settings)
    await mongo.connect()
    
    try:
        # Clean up test data before each test
        await mongo.db[test_settings.mongo_inventory_collection].delete_many({})
        yield mongo
    finally:
        # Clean up after each test
        await mongo.db[test_settings.mongo_inventory_collection].delete_many({})
        await mongo.close()


@pytest.fixture
def sample_inventory_data() -> dict:
    """Sample inventory data for testing."""
    return {
        "repo": "test-repo",
        "dependencias": [
            {
                "name": "requests",
                "version": "2.32.0",
                "ecosystem": "pip"
            },
            {
                "name": "react",
                "version": "18.2.0",
                "ecosystem": "npm"
            }
        ]
    }


@pytest.fixture
def sample_inventory_data_invalid() -> dict:
    """Sample invalid inventory data for testing validation."""
    return {
        "repo": "",  # Invalid: empty repo name
        "dependencias": [
            {
                "name": "test<script>",  # Invalid: contains script tag
                "version": "1.0.0",
                "ecosystem": "npm"
            }
        ]
    }


@pytest.fixture
def sample_alert_data() -> dict:
    """Sample alert data for testing."""
    return {
        "repo": "test-repo",
        "name": "requests",
        "version": "2.32.0",
        "cve_id": "CVE-2023-1234",
        "severity": "HIGH",
        "score": 8.5,
        "source": "NVD"
    }


# Mock external API responses
@pytest.fixture
def mock_nvd_response() -> dict:
    """Mock NVD API response."""
    return {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2023-1234",
                    "metrics": {
                        "cvssMetricV31": [
                            {
                                "cvssData": {
                                    "baseSeverity": "HIGH",
                                    "baseScore": 8.5
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }


@pytest.fixture
def mock_osv_response() -> dict:
    """Mock OSV API response."""
    return {
        "vulns": [
            {
                "id": "OSV-2023-1234",
                "aliases": ["CVE-2023-1234"]
            }
        ]
    }


# Test markers
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Environment setup for tests
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up environment variables for testing."""
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("JSON_LOGS", "false")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
