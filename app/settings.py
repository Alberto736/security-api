from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongo_uri: str = Field(alias="MONGO_URI")
    mongo_db: str = Field(default="hermod", alias="MONGO_DB")
    mongo_inventory_collection: str = Field(default="inventario", alias="MONGO_INVENTORY_COLLECTION")

    nvd_api_url: str = Field(default="https://services.nvd.nist.gov/rest/json/cves/2.0", alias="NVD_API_URL")
    nvd_api_key: str | None = Field(default=None, alias="NVD_API_KEY")
    user_agent: str = Field(default="security-api/0.1", alias="USER_AGENT")

    # API key de la empresa para proteger endpoints (ej: /inventario).
    # Si `API_KEY` no está definida, la API no aplicará auth (modo desarrollo).
    api_key: str | None = Field(default=None, alias="API_KEY")
    api_key_header: str = Field(default="X-API-Key", alias="API_KEY_HEADER")
    api_key_required: bool = Field(default=False, alias="API_KEY_REQUIRED")

    request_timeout_seconds: float = Field(default=10.0, alias="REQUEST_TIMEOUT_SECONDS")
    request_delay_seconds: float = Field(default=0.35, alias="REQUEST_DELAY_SECONDS")


def get_settings() -> Settings:
    return Settings()
