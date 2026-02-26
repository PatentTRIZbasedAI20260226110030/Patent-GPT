def test_settings_loads_defaults():
    """Settings should have sensible defaults even without .env file."""
    from app.config import Settings

    settings = Settings(
        OPENAI_API_KEY="test-key",
        KIPRIS_API_KEY="test-kipris",
    )
    assert settings.LLM_MODEL == "gpt-4o"
    assert settings.LLM_MODEL_MINI == "gpt-4o-mini"
    assert settings.EMBEDDING_MODEL == "text-embedding-3-small"
    assert settings.SIMILARITY_THRESHOLD == 0.8
    assert settings.MAX_EVASION_ATTEMPTS == 3
    assert settings.RETRIEVAL_TOP_K == 20
    assert settings.RERANK_TOP_K == 5


def test_settings_requires_api_keys(monkeypatch):
    """Settings should fail without required API keys."""
    import pytest
    from pydantic import ValidationError

    from app.config import Settings

    # Clear env vars that might satisfy the requirement
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValidationError):
        Settings()
