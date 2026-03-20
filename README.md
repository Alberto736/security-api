# Security API

[![CI/CD Pipeline](https://github.com/yourorg/security-api/actions/workflows/ci.yml/badge.svg)](https://github.com/yourorg/security-api/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/yourorg/security-api/branch/main/graph/badge.svg)](https://codecov.io/gh/yourorg/security-api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

FastAPI-based API for security vulnerability scanning and inventory management with MongoDB persistence.

## Features

- **Security**: API key authentication, rate limiting, input validation and sanitization
- **Monitoring**: Structured logging, comprehensive health checks, and error tracking
- **Testing**: Complete test suite with 80%+ coverage
- **CI/CD**: Automated pipeline with security scanning and quality gates
- **Production Ready**: Docker containerization with multi-environment support

## Requirements

- Docker + Docker Compose (recommended)
- Python 3.11+ (for local development)
- MongoDB 5.0+

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/yourorg/security-api.git
cd security-api
cp .env.example .env
# Edit .env with your configuration

docker compose up --build
```

### Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start MongoDB
docker run -d -p 27017:27017 --name mongo mongo:5.0

# Start API
uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

## API Documentation

### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/health` | Comprehensive health check | No |
| `GET` | `/health/simple` | Basic health check | No |
| `POST` | `/inventario` | Submit inventory for vulnerability scanning | Yes |
| `GET` | `/inventario` | List all inventories | Yes |
| `GET` | `/inventario/{repo}` | Get specific inventory | Yes |

### Authentication

Protected endpoints require an `X-API-Key` header:

```bash
curl -X POST "http://localhost:3000/inventario" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "repo": "example-repo",
    "dependencias": [
      {"name": "requests", "version": "2.32.0", "ecosystem": "pip"}
    ]
  }'
```

### Request/Response Examples

**Inventory Request:**
```json
{
  "repo": "example-repo",
  "dependencias": [
    {
      "name": "requests",
      "version": "2.32.0",
      "ecosystem": "pip"
    }
  ]
}
```

**Scan Response:**
```json
{
  "status": "ok",
  "repo": "example-repo",
  "alertas_encontradas": 1,
  "detalle": [
    {
      "repo": "example-repo",
      "name": "requests",
      "version": "2.32.0",
      "cve_id": "CVE-2023-1234",
      "severity": "HIGH",
      "score": 8.5,
      "source": "NVD"
    }
  ]
}
```

## Configuration

### Environment Variables

```bash
# Database
MONGO_URI=mongodb://user:password@localhost:27017/security_api
MONGO_DB=security_api
MONGO_INVENTORY_COLLECTION=inventory

# Security
API_KEY=your_secure_api_key
API_KEY_REQUIRED=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
JSON_LOGS=false

# CORS
CORS_ORIGINS=["*"]
```

### Production Configuration

Copy `.env.production` to `.env` and update with production values before deployment.

## Testing

```bash
# Unit tests
pytest tests/ -m "unit"

# Integration tests
pytest tests/ -m "integration"

# Coverage report
pytest tests/ --cov=app --cov-report=html
```

## Development

### Code Quality

```bash
# Linting
ruff check app/
ruff format app/

# Type checking
mypy app/

# Security scanning
bandit -r app/
```

### Pre-commit Setup

```bash
pre-commit install
pre-commit run --all-files
```

## Deployment

### Docker Production

```bash
cp .env.production .env
# Edit .env with production values

docker compose -f docker-compose.yml --env-file .env up -d
```

### Health Monitoring

```bash
# Comprehensive health check
curl http://localhost:3000/health

# Basic health check (for load balancers)
curl http://localhost:3000/health/simple
```

## Architecture

```
security-api/
├── app/
│   ├── middleware/          # Security and logging middleware
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   ├── schemas.py          # Pydantic models
│   ├── settings.py         # Configuration
│   └── logging_config.py   # Logging configuration
├── tests/                  # Test suite
├── .github/workflows/      # CI/CD pipeline
└── docker-compose.yml      # Docker configuration
```

## Security

- Input validation and sanitization against XSS and injection attacks
- API key-based authentication with configurable headers
- Rate limiting to prevent abuse and DoS attacks
- Structured logging for security event auditing
- CORS configuration for cross-origin protection

## License

MIT License - see [LICENSE](LICENSE) file for details.
