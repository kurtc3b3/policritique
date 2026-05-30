from policritique.settings import DEFAULT_CORS_ORIGINS, Settings


def test_default_cors_origins_include_vite(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    settings = Settings()

    assert "http://localhost:5173" in settings.cors_origins
    assert "http://127.0.0.1:5173" in settings.cors_origins


def test_cors_origins_parsed_from_env(monkeypatch):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "http://localhost:5173, http://example.com ",
    )
    settings = Settings()

    assert settings.cors_origins == ["http://localhost:5173", "http://example.com"]


def test_default_cors_origins_constant_matches_settings_default():
    settings = Settings(_env_file=None)
    assert settings.cors_origins_raw == DEFAULT_CORS_ORIGINS
