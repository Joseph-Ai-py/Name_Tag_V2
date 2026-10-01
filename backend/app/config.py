from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NAME TAG"
    app_env: str = "development"
    debug: bool = True

    database_url: str = "sqlite:///./name_tag.db"
    llm_provider: str = "mock"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3-flash-preview"

    session_cookie_name: str = "name_tag_session"
    session_cookie_secure: bool = False
    session_cookie_http_only: bool = True
    session_cookie_same_site: str = "lax"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()