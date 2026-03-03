def test_settings_loads_defaults():
    """Settings should have sensible defaults even without .env file."""
    from app.config import Settings

    settings = Settings(
        GOOGLE_API_KEY="test-google-key",
    )
    assert settings.GEMINI_MODEL == "gemini-2.0-flash"
    assert settings.EMBEDDING_MODEL == "text-embedding-3-small"
    assert settings.SIMILARITY_THRESHOLD == 0.5
    assert settings.MAX_EVASION_ATTEMPTS == 3
    assert settings.RETRIEVAL_TOP_K == 20
    assert settings.RERANK_TOP_K == 5


def test_settings_requires_google_api_key(monkeypatch):
    """Settings should fail without required GOOGLE_API_KEY."""
    import pytest
    from pydantic import ValidationError

    from app.config import Settings

    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
