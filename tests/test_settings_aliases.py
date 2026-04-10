from packages.core.config import get_settings


def test_settings_accepts_bmt_api_environment_alias(monkeypatch) -> None:
    monkeypatch.setenv("BMT_API_ENVIRONMENT", "production")
    monkeypatch.delenv("BMT_API_ENV", raising=False)
    monkeypatch.delenv("BMT_API_DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = get_settings()

    assert settings.environment == "production"


def test_settings_accepts_bmt_api_env_alias(monkeypatch) -> None:
    monkeypatch.setenv("BMT_API_ENV", "production")
    monkeypatch.delenv("BMT_API_ENVIRONMENT", raising=False)
    monkeypatch.delenv("BMT_API_DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = get_settings()

    assert settings.environment == "production"


def test_settings_accepts_database_url_alias(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    monkeypatch.delenv("BMT_API_DATABASE_URL", raising=False)

    settings = get_settings()

    assert settings.database_url == "postgresql+psycopg://user:pass@host:5432/db"
