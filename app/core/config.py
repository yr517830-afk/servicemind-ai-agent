from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ServiceMind 项目配置。"""

    app_name: str = "ServiceMind AI Agent"
    app_version: str = "0.1.0"
    debug: bool = False
    database_path: str = "data/servicemind.db"
    database_url: str = "sqlite:///data/servicemind.db"
    routing_rules_path: str = "config/routing_rules.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """创建并缓存项目配置对象。"""
    return Settings()


settings = get_settings()