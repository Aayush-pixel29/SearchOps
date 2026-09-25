"""SearchOps configuration. Providers are selected by env, never hardcoded in ranking logic."""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    env: str = "local"
    secret_key: str = Field(
        default="dev-only-not-for-production",
        validation_alias=AliasChoices("SEARCHOPS_SECRET_KEY", "SECRET_KEY"),
    )
    access_token_expire_minutes: int = 720

    database_url: str = Field(
        default="sqlite+aiosqlite:///./searchops.db",
        validation_alias=AliasChoices("DATABASE_URL", "SEARCHOPS_DATABASE_URL"),
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("REDIS_URL", "SEARCHOPS_REDIS_URL"),
    )
    cache_ttl_seconds: int = 60

    embedding_provider: str = "hashed"
    embedding_dim: int = 384
    openai_api_key: str = Field(default="", validation_alias=AliasChoices("OPENAI_API_KEY"))
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    gemini_api_key: str = Field(default="", validation_alias=AliasChoices("GEMINI_API_KEY"))
    gemini_embedding_model: str = "text-embedding-004"
    gemini_chat_model: str = "gemini-2.0-flash"
    hf_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    llm_provider: str = "none"
    reranker: str = "heuristic"
    hybrid_alpha: float = 0.6

    demo_seed: bool = True
    demo_email: str = "demo@searchops.dev"
    demo_password: str = "demo-password"


@lru_cache
def get_settings() -> Settings:
    return Settings()
