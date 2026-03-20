# Security API - Versión Simplificada

API para notificaciones de vulnerabilidades diseñada para uso empresarial con el balance adecuado entre simplicidad y robustez.

## 🎯 Enfoque: "Simple pero Seguro"

Esta versión mantiene lo esencial para producción enterprise sin sobre-ingeniería:

### ✅ **Mantenido (Esencial)**
- **Validación de entrada** - Protección contra ataques
- **Logging básico** - Debugging y auditoría
- **Health checks** - Monitoreo de producción
- **API key auth** - Seguridad básica
- **Rate limiting simple** - Protección DoS
- **Tests unitarios** - Estabilidad garantizada

### ❌ **Simplificado (Removido)**
- Rate limiting complejo con slowapi
- CI/CD pipeline completo
- Coverage 80%+ (reducido a 60%)
- Múltiples middleware complejos
- Logging estructurado avanzado

## 🚀 Quick Start

```bash
# 1. Configurar
cp .env.example .env
# Editar API_KEY y otras variables

# 2. Ejecutar
docker compose up --build

# 3. Probar
curl http://localhost:3000/health/simple
```

## 📚 Endpoints Clave

| Endpoint | Método | Auth | Descripción |
|----------|--------|------|-------------|
| `/health/simple` | GET | ❌ | Health check básico |
| `/inventario` | POST | ✅ | Recibir inventario |
| `/inventario` | GET | ✅ | Listar inventarios |
| `/inventario/{repo}` | GET | ✅ | Obtener inventario |

## 🛡️ Seguridad Esencial

```bash
# Configuración mínima segura
API_KEY=tu_api_key_secreta_32_chars
API_KEY_REQUIRED=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=60
```

## 🧪 Testing Simplificado

```bash
# Tests rápidos
pytest tests/test_api.py -v

# Coverage básico
pytest --cov=app --cov-report=term-missing
```

## 📊 Métricas Apropiadas

- **Coverage**: 60-70% (suficiente para API simple)
- **Tests**: Unitarios + integración básica
- **Security**: Validación + rate limiting
- **Monitoring**: Health checks + logging

## 🚦 ¿Por qué esta versión?

### Para uso empresarial:
- ✅ **Estable** - Tests y validación robustos
- ✅ **Seguro** - Protección contra ataques comunes
- ✅ **Mantenible** - Código simple y claro
- ✅ **Escalable** - Arquitectura limpia

### Sin over-engineering:
- ❌ Complejidad innecesaria
- ❌ Herramientas excesivas
- ❌ Configuración complicada
- ❌ Pipeline demasiado grande

## 🎯 Conclusión

**Perfecto para**: Empresas que necesitan una API de vulnerabilidades estable y segura sin la complejidad de un proyecto enterprise-grade.

**No ideal para**: Startups que necesitan features avanzadas o empresas con requisitos de compliance muy estrictos.

> **Regla general**: Si tu equipo puede mantenerlo y entiende todo el código, está bien. Si se vuelve complejo de entender o mantener, es demasiado.
