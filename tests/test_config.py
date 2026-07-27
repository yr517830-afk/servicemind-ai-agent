from pytest import MonkeyPatch

from app.core.config import Settings


def test_default_settings() -> None:
    """没有环境变量时应使用默认配置。"""
    settings = Settings(_env_file=None)

    assert settings.app_name == "ServiceMind AI Agent"
    assert settings.app_version == "0.1.0"
    assert settings.debug is False
    assert settings.database_path == "data/servicemind.db"
    assert settings.routing_rules_path == "config/routing_rules.json"
    assert settings.database_url == "sqlite:///data/servicemind.db"


def test_settings_read_environment_variables(
    monkeypatch: MonkeyPatch,
) -> None:
    """环境变量应能覆盖默认配置。"""
    monkeypatch.setenv("APP_NAME", "ServiceMind Test API")
    monkeypatch.setenv("APP_VERSION", "9.9.9")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://test:test@localhost:5432/test_db",
    )

    settings = Settings(_env_file=None)

    assert settings.app_name == "ServiceMind Test API"
    assert settings.app_version == "9.9.9"
    assert settings.debug is True
    assert settings.database_url == (
        "postgresql+psycopg://test:test@localhost:5432/test_db"
    )