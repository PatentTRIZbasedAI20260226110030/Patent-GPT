import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from app.api.schemas.request import PatentGenerateRequest, PatentSearchRequest
from app.api.schemas.response import PatentGenerateResponse, PatentSearchResponse
from app.config import Settings, get_settings
from app.models.state import AgentState
from app.services.patent_searcher import PatentSearcher
from app.services.patent_service import PatentService
from app.services.reasoning_agent import PatentPipeline

router = APIRouter(prefix="/patent")


def get_patent_service(settings: Settings = Depends(get_settings)) -> PatentService:
    return PatentService(settings)


def get_patent_searcher(settings: Settings = Depends(get_settings)) -> PatentSearcher:
    return PatentSearcher(settings)


def get_pipeline(settings: Settings = Depends(get_settings)) -> PatentPipeline:
    return PatentPipeline(settings)


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


@router.post("/generate/stream")
async def generate_patent_stream(
    request: PatentGenerateRequest,
    pipeline: PatentPipeline = Depends(get_pipeline),
):
    """SSE endpoint that streams step-by-step LangGraph state updates."""

    initial_state: AgentState = {
        "user_problem": request.problem_description,
        "technical_field": request.technical_field or "",
        "triz_principles": [],
        "current_idea": "",
        "similar_patents": [],
        "max_similarity_score": 0.0,
        "novelty_score": 0.0,
        "novelty_reasoning": "",
        "context_sufficient": False,
        "evasion_count": 0,
        "final_idea": "",
        "reasoning_trace": [],
        "current_step": "",
    }

    async def event_generator():
        async for event in pipeline.stream(initial_state):
            # LangGraph astream yields dicts keyed by node name
            for node_name, node_state in event.items():
                yield {
                    "event": "step",
                    "data": json.dumps(
                        {"step": node_name, "state": _serialize_state(node_state)},
                        ensure_ascii=False,
                    ),
                }
        yield {"event": "done", "data": "{}"}

    return EventSourceResponse(event_generator())


def _serialize_state(state: dict) -> dict:
    """Convert state to JSON-serializable dict."""
    result = {}
    for key, value in state.items():
        if hasattr(value, "model_dump"):
            result[key] = value.model_dump()
        elif isinstance(value, list) and value and hasattr(value[0], "model_dump"):
            result[key] = [item.model_dump() for item in value]
        else:
            result[key] = value
    return result


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
