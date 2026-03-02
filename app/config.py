from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: str  # required, for Gemini LLM
    OPENAI_API_KEY: str = ""  # optional, for embeddings only
    KIPRIS_API_KEY: str = ""

    # Model settings
    GEMINI_MODEL: str = "gemini-3-flash-preview"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Search settings
    SIMILARITY_THRESHOLD: float = 0.5
    MAX_EVASION_ATTEMPTS: int = 3
    RETRIEVAL_TOP_K: int = 20
    RERANK_TOP_K: int = 5

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chromadb"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "extra": "ignore"}


def get_settings() -> Settings:
    return Settings()
