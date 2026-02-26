from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(
    title="Patent-GPT",
    description="Agentic RAG-based invention copilot combining TRIZ methodology with LLMs",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api/v1")
