from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    KIPRIS_API_KEY: str = ""

    # Model settings
    LLM_MODEL: str = "gpt-4o"
    LLM_MODEL_MINI: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Search settings
    SIMILARITY_THRESHOLD: float = 0.8
    MAX_EVASION_ATTEMPTS: int = 3
    RETRIEVAL_TOP_K: int = 20
    RERANK_TOP_K: int = 5

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./data/chromadb"

    model_config = {"env_file": ".env", "extra": "ignore"}


def get_settings() -> Settings:
    return Settings()
