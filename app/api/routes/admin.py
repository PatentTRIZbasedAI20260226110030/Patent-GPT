from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.config import Settings, get_settings

router = APIRouter(prefix="/admin")


class IngestRequest(BaseModel):
    keyword: str = Field(min_length=1, description="검색 키워드")
    max_patents: int = Field(default=100, ge=1, le=500)


class IngestResponse(BaseModel):
    ingested_count: int
    status: str


@router.post("/ingest", response_model=IngestResponse)
async def ingest_patents(
    request: IngestRequest,
    settings: Settings = Depends(get_settings),
):
    try:
        from scripts.ingest_patents import ingest
        count = await ingest(request.keyword, request.max_patents)
        return IngestResponse(ingested_count=count, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
