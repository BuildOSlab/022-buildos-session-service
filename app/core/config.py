from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BuildOS Session Service"
    app_version: str = "0.1.0"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://localhost/buildos_session"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
