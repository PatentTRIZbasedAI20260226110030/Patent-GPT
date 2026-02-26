from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.api.schemas.request import PatentGenerateRequest, PatentSearchRequest
from app.api.schemas.response import PatentGenerateResponse, PatentSearchResponse
from app.config import Settings, get_settings
from app.services.patent_searcher import PatentSearcher
from app.services.patent_service import PatentService

router = APIRouter(prefix="/patent")


def get_patent_service(settings: Settings = Depends(get_settings)) -> PatentService:
    return PatentService(settings)


def get_patent_searcher(settings: Settings = Depends(get_settings)) -> PatentSearcher:
    return PatentSearcher(settings)


@router.post("/generate", response_model=PatentGenerateResponse)
async def generate_patent(
    request: PatentGenerateRequest,
    service: PatentService = Depends(get_patent_service),
):
    try:
        return await service.generate(
            problem_description=request.problem_description,
            technical_field=request.technical_field,
            max_evasion_attempts=request.max_evasion_attempts,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=PatentSearchResponse)
async def search_patents(
    request: PatentSearchRequest,
    searcher: PatentSearcher = Depends(get_patent_searcher),
):
    try:
        results = await searcher.search(request.query, top_k=request.top_k)
        return PatentSearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{draft_id}/docx")
async def download_docx(draft_id: str):
    docx_path = Path(f"data/drafts/{draft_id}.docx")
    if not docx_path.exists():
        raise HTTPException(status_code=404, detail="DOCX file not found")
    return FileResponse(
        path=str(docx_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"patent_draft_{draft_id}.docx",
    )
