"""
Central settings object. Every credential the Hub needs (DB, Redis, AI
provider keys, Stripe, Turnstile, R2, Resend) is read here from the
environment — never hardcoded, never passed to the WordPress plugin.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    # Core infra
    database_url: str = "postgresql+psycopg://smashfire:smashfire@localhost:5432/smashfire_hub"
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    hub_jwt_secret: str = "dev-only-change-me"

    # AI providers — Hub-only, never exposed to the plugin
    deepseek_api_key: str | None = None
    openai_api_key: str | None = None
    gemini_api_key: str | None = None

    # Third parties, wired in during later phases
    stripe_secret_key: str | None = None
    cloudflare_turnstile_secret: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: str | None = None
    resend_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
