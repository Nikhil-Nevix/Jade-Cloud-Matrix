from typing import Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    # App
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    CORS_ORIGINS: Union[str, list[str]] = "http://localhost:5173,http://localhost:3000"

    # AI
    ANTHROPIC_API_KEY: str = ""

    # Cloud APIs (optional)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_DEFAULT_REGION: str = "us-east-1"
    AZURE_SUBSCRIPTION_ID: str = ""
    AZURE_TENANT_ID: str = ""
    GCP_PROJECT_ID: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""  # Path to GCP service account JSON file

    # Pricing API Mode
    PRICING_API_MODE: str = "fallback"  # Options: "live", "fallback", "hybrid"

    # Ingestion
    INGESTION_HOUR: int = 2
    INGESTION_MINUTE: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


settings = Settings()
