from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # MongoDB settings
    mongo_uri: str = Field(alias="MONGO_URI")
    mongo_db: str = Field(default="hermod", alias="MONGO_DB")
    mongo_inventory_collection: str = Field(default="inventario", alias="MONGO_INVENTORY_COLLECTION")

    # External API settings
    nvd_api_url: str = Field(default="https://services.nvd.nist.gov/rest/json/cves/2.0", alias="NVD_API_URL")
    nvd_api_key: str | None = Field(default=None, alias="NVD_API_KEY")
    user_agent: str = Field(default="security-api/0.1", alias="USER_AGENT")

    # API key security settings
    api_key: str | None = Field(default=None, alias="API_KEY")
    api_key_header: str = Field(default="X-API-Key", alias="API_KEY_HEADER")
    api_key_required: bool = Field(default=False, alias="API_KEY_REQUIRED")

    # Request settings
    request_timeout_seconds: float = Field(default=10.0, alias="REQUEST_TIMEOUT_SECONDS")
    request_delay_seconds: float = Field(default=0.35, alias="REQUEST_DELAY_SECONDS")

    # Rate limiting settings
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")  # seconds

    # Logging settings
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    json_logs: bool = Field(default=False, alias="JSON_LOGS")

    # Security settings
    cors_origins: list[str] = Field(default=["*"], alias="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    max_request_size: int = Field(default=10 * 1024 * 1024, alias="MAX_REQUEST_SIZE")  # 10MB

    # Production settings
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")


def get_settings() -> Settings:
    return Settings()
