"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the API service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    database_url: str = Field(
        default="postgresql+psycopg://spacebio:spacebio@localhost:5432/spacebio",
        alias="DATABASE_URL",
    )
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    ollama_base_url: str = Field(
        default="http://127.0.0.1:11434/v1",
        alias="OLLAMA_BASE_URL",
    )
    ollama_model: str = Field(default="llama3.2:1b", alias="OLLAMA_MODEL")
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
    )
    # Developer retrieval diagnostics UI/API (issue #67). Off by default.
    dev_retrieval_diagnostics: bool = Field(
        default=False,
        alias="SPACEBIO_DEV_RETRIEVAL_DIAGNOSTICS",
    )
    # Optional lexical rerank after retrieval (issue #48). Off by default.
    rerank_enabled: bool = Field(default=False, alias="SPACEBIO_RERANK_ENABLED")
    reranker: str = Field(default="lexical_overlap", alias="SPACEBIO_RERANKER")
    pdf_storage_local_root: str = Field(
        default="data/pdfs",
        alias="PDF_STORAGE_LOCAL_ROOT",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
