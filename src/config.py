"""
Global Configuration Settings.
Loads and validates environment variables using Pydantic Settings.
"""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # Application details
    environment: Literal["local", "development", "staging", "production"] = "local"
    debug: bool = False
    allowed_origins: list[str] = Field(default=["http://localhost:3000"])

    # Relational & Vector Storage (Postgres + pgvector)
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/git_graph_dev"
    )

    # Cache & Celery Message Broker
    redis_url: str = Field(default="redis://localhost:6379/0")

    # LLM Provider Configuration
    llm_provider: Literal["openai", "anthropic", "ollama"] = "openai"
    llm_api_key: str | None = None
    llm_model: str = "gpt-4o"
    
    # Embedding Configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Repository Storage Paths
    storage_root: str = "./data/repositories"


settings = Settings()
