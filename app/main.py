from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin import router as admin_router
from app.api.routes.health import router as health_router
from app.api.routes.patent import router as patent_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Patent-GPT",
    description="Agentic RAG-based invention copilot combining TRIZ methodology with LLMs",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(patent_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
