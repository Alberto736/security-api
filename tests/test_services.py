"""
Unit tests for service layer components.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.services.nvd import query_nvd, NvdFinding, _parse_severity
from app.services.osv import query_osv, OsvFinding
from app.services.http import request_with_retries


class TestNVDService:
    """Test NVD service functionality."""
    
    @pytest.mark.unit
    async def test_query_nvd_success(self):
        """Test successful NVD query."""
        mock_settings = MagicMock()
        mock_settings.nvd_api_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        mock_settings.nvd_api_key = "test_key"
        mock_settings.user_agent = "security-api/0.1"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
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
        
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        
        with patch('app.services.nvd.request_with_retries', return_value=mock_response):
            findings = await query_nvd(mock_settings, mock_client, "requests")
        
        assert len(findings) == 1
        finding = findings[0]
        assert isinstance(finding, NvdFinding)
        assert finding.cve_id == "CVE-2023-1234"
        assert finding.severity == "HIGH"
        assert finding.score == 8.5
    
    @pytest.mark.unit
    async def test_query_nvd_no_api_key(self):
        """Test NVD query without API key."""
        mock_settings = MagicMock()
        mock_settings.nvd_api_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        mock_settings.nvd_api_key = None
        mock_settings.user_agent = "security-api/0.1"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"vulnerabilities": []}
        
        mock_client = AsyncMock()
        
        with patch('app.services.nvd.request_with_retries', return_value=mock_response):
            findings = await query_nvd(mock_settings, mock_client, "requests")
        
        assert len(findings) == 0
    
    @pytest.mark.unit
    async def test_query_nvd_error(self):
        """Test NVD query with error."""
        mock_settings = MagicMock()
        mock_settings.nvd_api_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        mock_settings.nvd_api_key = "test_key"
        mock_settings.user_agent = "security-api/0.1"
        
        mock_client = AsyncMock()
        
        with patch('app.services.nvd.request_with_retries', side_effect=Exception("Network error")):
            findings = await query_nvd(mock_settings, mock_client, "requests")
        
        assert len(findings) == 0
    
    @pytest.mark.unit
    def test_parse_severity_cvss_v31(self):
        """Test parsing severity with CVSS v3.1."""
        vuln = {
            "cve": {
                "metrics": {
                    "cvssMetricV31": [
                        {
                            "cvssData": {
                                "baseSeverity": "CRITICAL",
                                "baseScore": 9.8
                            }
                        }
                    ]
                }
            }
        }
        
        severity, score = _parse_severity(vuln)
        assert severity == "CRITICAL"
        assert score == 9.8
    
    @pytest.mark.unit
    def test_parse_severity_cvss_v30(self):
        """Test parsing severity with CVSS v3.0."""
        vuln = {
            "cve": {
                "metrics": {
                    "cvssMetricV30": [
                        {
                            "cvssData": {
                                "baseSeverity": "HIGH",
                                "baseScore": 8.2
                            }
                        }
                    ]
                }
            }
        }
        
        severity, score = _parse_severity(vuln)
        assert severity == "HIGH"
        assert score == 8.2
    
    @pytest.mark.unit
    def test_parse_severity_cvss_v2(self):
        """Test parsing severity with CVSS v2."""
        vuln = {
            "cve": {
                "metrics": {
                    "cvssMetricV2": [
                        {
                            "baseSeverity": "MEDIUM",
                            "baseScore": 6.5
                        }
                    ]
                }
            }
        }
        
        severity, score = _parse_severity(vuln)
        assert severity == "MEDIUM"
        assert score == 6.5
    
    @pytest.mark.unit
    def test_parse_severity_no_metrics(self):
        """Test parsing severity with no metrics."""
        vuln = {"cve": {}}
        
        severity, score = _parse_severity(vuln)
        assert severity == "UNKNOWN"
        assert score == 0.0
    
    @pytest.mark.unit
    def test_parse_severity_malformed_data(self):
        """Test parsing severity with malformed data."""
        vuln = {
            "cve": {
                "metrics": {
                    "cvssMetricV31": [
                        {
                            "cvssData": {}  # Missing severity and score
                        }
                    ]
                }
            }
        }
        
        severity, score = _parse_severity(vuln)
        assert severity == "UNKNOWN"
        assert score == 0.0


class TestOSVService:
    """Test OSV service functionality."""
    
    @pytest.mark.unit
    async def test_query_osv_success(self):
        """Test successful OSV query."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "vulns": [
                {
                    "id": "OSV-2023-1234",
                    "aliases": ["CVE-2023-1234"]
                }
            ]
        }
        
        mock_client = AsyncMock()
        
        with patch('app.services.osv.request_with_retries', return_value=mock_response):
            findings = await query_osv(mock_client, name="requests", version="2.32.0", ecosystem="pip")
        
        assert len(findings) == 1
        finding = findings[0]
        assert isinstance(finding, OsvFinding)
        assert finding.cve_id == "CVE-2023-1234"
    
    @pytest.mark.unit
    async def test_query_osv_no_version(self):
        """Test OSV query without version."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"vulns": []}
        
        mock_client = AsyncMock()
        
        with patch('app.services.osv.request_with_retries', return_value=mock_response):
            findings = await query_osv(mock_client, name="requests", version=None, ecosystem="pip")
        
        assert len(findings) == 0
    
    @pytest.mark.unit
    async def test_query_osv_unsupported_ecosystem(self):
        """Test OSV query with unsupported ecosystem."""
        mock_client = AsyncMock()
        
        findings = await query_osv(mock_client, name="package", version="1.0.0", ecosystem="unsupported")
        
        assert len(findings) == 0
    
    @pytest.mark.unit
    async def test_query_osv_no_cve_alias(self):
        """Test OSV query without CVE alias."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "vulns": [
                {
                    "id": "OSV-2023-1234",
                    "aliases": []  # No CVE alias
                }
            ]
        }
        
        mock_client = AsyncMock()
        
        with patch('app.services.osv.request_with_retries', return_value=mock_response):
            findings = await query_osv(mock_client, name="requests", version="2.32.0", ecosystem="pip")
        
        assert len(findings) == 1
        finding = findings[0]
        assert finding.cve_id == "OSV-2023-1234"
    
    @pytest.mark.unit
    async def test_query_osv_error(self):
        """Test OSV query with error."""
        mock_client = AsyncMock()
        
        with patch('app.services.osv.request_with_retries', side_effect=Exception("Network error")):
            findings = await query_osv(mock_client, name="requests", version="2.32.0", ecosystem="pip")
        
        assert len(findings) == 0
    
    @pytest.mark.unit
    def test_ecosystem_mapping(self):
        """Test ecosystem name mapping."""
        from app.services.osv import _ECOSYSTEM_MAP
        
        assert _ECOSYSTEM_MAP["npm"] == "npm"
        assert _ECOSYSTEM_MAP["pip"] == "PyPI"
        assert _ECOSYSTEM_MAP["maven"] == "Maven"
        assert _ECOSYSTEM_MAP["gradle"] == "Maven"
        assert _ECOSYSTEM_MAP["composer"] == "Packagist"
        assert _ECOSYSTEM_MAP["nuget"] == "NuGet"
        assert _ECOSYSTEM_MAP["rubygems"] == "RubyGems"
        assert _ECOSYSTEM_MAP["cargo"] == "crates.io"
        assert _ECOSYSTEM_MAP["golang"] == "Go"
        assert _ECOSYSTEM_MAP["docker"] == "Docker"


class TestHTTPService:
    """Test HTTP service functionality."""
    
    @pytest.mark.unit
    async def test_request_with_retries_success(self):
        """Test successful request with retries."""
        mock_response = MagicMock()
        mock_make_request = AsyncMock(return_value=mock_response)
        
        result = await request_with_retries(mock_make_request)
        
        assert result == mock_response
        assert mock_make_request.call_count == 1
    
    @pytest.mark.unit
    async def test_request_with_retries_timeout_error(self):
        """Test request with timeout error and retries."""
        mock_make_request = AsyncMock(side_effect=[
            httpx.TimeoutException("Timeout"),
            httpx.TimeoutException("Timeout"),
            MagicMock()  # Success on third try
        ])
        
        result = await request_with_retries(mock_make_request, retries=2)
        
        assert result is not None
        assert mock_make_request.call_count == 3
    
    @pytest.mark.unit
    async def test_request_with_retries_exhausted(self):
        """Test request with exhausted retries."""
        mock_make_request = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        
        with pytest.raises(httpx.TimeoutException):
            await request_with_retries(mock_make_request, retries=2)
        
        assert mock_make_request.call_count == 3  # Initial + 2 retries
    
    @pytest.mark.unit
    async def test_request_with_retries_network_error(self):
        """Test request with network error and retries."""
        mock_make_request = AsyncMock(side_effect=[
            httpx.NetworkError("Network error"),
            MagicMock()  # Success on second try
        ])
        
        result = await request_with_retries(mock_make_request, retries=2)
        
        assert result is not None
        assert mock_make_request.call_count == 2
    
    @pytest.mark.unit
    async def test_request_with_retries_custom_backoff(self):
        """Test request with custom backoff configuration."""
        mock_make_request = AsyncMock(side_effect=[
            httpx.TimeoutException("Timeout"),
            MagicMock()  # Success on second try
        ])
        
        import time
        start_time = time.time()
        
        result = await request_with_retries(
            mock_make_request, 
            retries=1, 
            base_backoff_seconds=0.1
        )
        
        elapsed_time = time.time() - start_time
        
        assert result is not None
        assert mock_make_request.call_count == 2
        assert elapsed_time >= 0.1  # Should have waited for backoff
    
    @pytest.mark.unit
    async def test_request_with_retries_different_exceptions(self):
        """Test request with different retryable exceptions."""
        exceptions = [
            httpx.RemoteProtocolError("Protocol error"),
            httpx.NetworkError("Network error"),
            MagicMock()  # Success
        ]
        
        mock_make_request = AsyncMock(side_effect=exceptions)
        
        result = await request_with_retries(mock_make_request, retries=2)

        assert result is not None
        assert mock_make_request.call_count == 3
