from functools import lru_cache
from typing import Literal

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic_settings import BaseSettings

__version__ = "0.1.0"


class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: str = ""  # optional, kept for backwards compat
    OPENAI_API_KEY: str  # required, for LLM + embeddings
    KIPRIS_API_KEY: str = ""

    # Model settings
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Search settings
    SIMILARITY_THRESHOLD: float = 0.5
    MAX_EVASION_ATTEMPTS: int = 3
    RETRIEVAL_TOP_K: int = 20
    RERANK_TOP_K: int = 5

    # TRIZ classifier routing
    TRIZ_ROUTER: Literal["llm", "ml"] = "llm"
    ML_MODEL_PATH: str = "./data/models/triz_classifier.joblib"

    # Evaluation
    FAITHFULNESS_THRESHOLD: float = 0.8
    ENABLE_AUTO_EVALUATION: bool = False

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chromadb"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_llm(settings: Settings, temperature: float = 0.7) -> ChatOpenAI:
    """Centralized LLM factory. All LLM calls go through here."""
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=temperature,
    )


def get_embeddings(settings: Settings) -> OpenAIEmbeddings:
    """Centralized embeddings factory."""
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )
