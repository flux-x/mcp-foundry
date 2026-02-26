from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    APP_NAME: str = Field(default="mcp-foundry")
    ENV: str = Field(default="local")

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    )
    DATABASE_SYNC_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
    )

    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_API_KEY: str | None = Field(default=None)

    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2")
    EMBEDDING_DIM: int = Field(default=384)

    SCRAPING_MAX_PAGES: int = Field(default=100)


settings = Settings()
