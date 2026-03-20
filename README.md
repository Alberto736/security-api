# security-api

API en FastAPI para recibir un inventario de dependencias y consultar vulnerabilidades (NVD/OSV). Incluye MongoDB para persistir inventarios.

## Requisitos

- Docker + Docker Compose (recomendado), o Python 3.11+

## Ejecutar con Docker

1. Levanta MongoDB y la API:

```bash
docker compose up --build
```

2. La API queda en `http://localhost:3000` y el Swagger UI en `http://localhost:3000/docs`.

## Ejecutar en local (sin Docker)

1. Crea un `.env` basado en `.env.example` y ajusta `MONGO_URI`.
2. Si cambias credenciales, asegúrate de que `MONGO_URI` use el mismo usuario y password que configuraste en Mongo.
3. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Arranca la API:

```bash
uvicorn main:app --host 0.0.0.0 --port 3000
```

## Endpoints

- `GET /health`: indica que la API está funcionando.
- `POST /inventario`: guarda un inventario de dependencias y devuelve alertas.
- `GET /inventario`: lista inventarios guardados.
- `GET /inventario/{repo}`: obtiene el inventario de un repo.

## Autenticacion (API Key)

Si configuras `API_KEY` en el entorno (por ejemplo en `docker-compose.yml` / `.env`), la API requiere un header:

- `X-API-Key: <tu_api_key>`

Rutas protegidas: `POST /inventario`, `GET /inventario`, `GET /inventario/{repo}`.

## Nota de Mongo (usuarios)

El contenedor Mongo crea un usuario de aplicación (`user/password`) en la base `hermod` usando el script `init-mongo.js`.

Ejemplo (POST):

```bash
curl -X POST "http://localhost:3000/inventario" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: TU_API_KEY" \
  -d "{\"repo\":\"mi-repo\",\"dependencias\":[{\"name\":\"requests\",\"version\":\"2.32.0\",\"ecosystem\":\"pip\"}]}"
```

### Ejemplo de payload

```json
{
  "repo": "mi-repo",
  "dependencias": [
    { "name": "requests", "version": "2.32.0", "ecosystem": "pip" }
  ]
}
```
