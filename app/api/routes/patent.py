import json
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from app.api.schemas.request import (
    PatentEvaluateRequest,
    PatentGenerateRequest,
    PatentSearchRequest,
)
from app.api.schemas.response import PatentGenerateResponse, PatentSearchResponse
from app.config import Settings, get_settings
from app.models.evaluation import EvaluationResult
from app.models.session import SessionStore
from app.models.state import build_initial_state
from app.services.evaluation_service import evaluate_pipeline_output
from app.services.patent_searcher import PatentSearcher
from app.services.patent_service import PatentService
from app.services.reasoning_agent import PatentPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patent")

# Module-level singleton session store
_session_store = SessionStore(max_sessions=100, ttl_seconds=3600)


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
        # Session management
        session_id = request.session_id or str(uuid.uuid4())
        session = _session_store.get_or_create(session_id)
        session.add_turn("user", request.problem_description)

        result = await service.generate(
            problem_description=request.problem_description,
            keyword=request.keyword,
            technical_field=request.technical_field,
            max_evasion_attempts=request.max_evasion_attempts,
        )

        # Record assistant turn
        summary = result.patent_draft.title if result.patent_draft else "생성 완료"
        session.add_turn("assistant", summary)

        result.session_id = session_id
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/stream")
async def generate_patent_stream(
    request: PatentGenerateRequest,
    pipeline: PatentPipeline = Depends(get_pipeline),
    settings: Settings = Depends(get_settings),
):
    """SSE endpoint that streams step-by-step LangGraph state updates."""

    initial_state = build_initial_state(
        problem_description=request.problem_description,
        keyword=request.keyword or "",
        technical_field=request.technical_field or "",
        max_evasion_attempts=request.max_evasion_attempts,
    )

    async def event_generator():
        accumulated = dict(initial_state)
        try:
            async for event in pipeline.stream(initial_state):
                for node_name, node_state in event.items():
                    accumulated.update(node_state)
                    yield {
                        "event": "step",
                        "data": json.dumps(
                            {"step": node_name, "state": _serialize_state(node_state)},
                            ensure_ascii=False,
                        ),
                    }

            # Build final response from accumulated state
            draft = accumulated.get("patent_draft")
            docx_path = accumulated.get("docx_path")
            draft_id = Path(docx_path).stem if docx_path else None
            response = {
                "patent_draft": draft.model_dump() if draft else None,
                "triz_principles": [
                    p.model_dump() for p in accumulated.get("triz_principles", [])
                ],
                "similar_patents": [
                    p.model_dump() for p in accumulated.get("similar_patents", [])
                ],
                "reasoning_trace": accumulated.get("reasoning_trace", []),
                "draft_id": draft_id,
                "novelty_score": accumulated.get("novelty_score"),
                "threshold": settings.SIMILARITY_THRESHOLD,
                "docx_download_url": (
                    f"/api/v1/patent/{draft_id}/docx" if draft_id else None
                ),
            }
            yield {"event": "done", "data": json.dumps(response, ensure_ascii=False)}
        except Exception as exc:
            logger.exception("Pipeline streaming error: %s", exc)
            yield {
                "event": "error",
                "data": json.dumps(
                    {
                        "message": str(exc),
                        "step": accumulated.get("current_step", "unknown"),
                    },
                    ensure_ascii=False,
                ),
            }

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


@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate_patent(
    request: PatentEvaluateRequest,
    settings: Settings = Depends(get_settings),
):
    """Run RAGAS evaluation on a pipeline result."""
    try:
        reference = request.reference or request.generated_idea
        return await evaluate_pipeline_output(
            user_problem=request.user_problem,
            generated_idea=request.generated_idea,
            retrieved_contexts=request.retrieved_contexts,
            reference=reference,
            settings=settings,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """Retrieve conversation history for a session."""
    session = _session_store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session.session_id,
        "turns": [t.model_dump() for t in session.turns],
        "created_at": session.created_at,
    }


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its conversation history."""
    deleted = _session_store.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"detail": "Session deleted"}


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
