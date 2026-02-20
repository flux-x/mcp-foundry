from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    APP_NAME: str = Field(default="mcp-foundry")
    ENV: str = Field(default="local")
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
    )
    SECRET_KEY: str = Field(default="insecure")


settings = Settings()
