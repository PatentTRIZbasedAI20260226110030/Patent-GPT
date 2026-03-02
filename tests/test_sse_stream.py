"""E2E integration tests for the SSE streaming pipeline.

Validates POST /api/v1/patent/generate/stream — step events, done event,
error handling, input validation, and CORS headers.
"""

from __future__ import annotations

import json

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.routes.patent import get_pipeline
from app.main import app
from app.models.patent_draft import PatentDraft, SimilarPatent
from app.models.triz import TRIZPrinciple

# ── Helpers ────────────────────────────────────────────────────────


def _make_mock_draft() -> PatentDraft:
    return PatentDraft(
        title="테스트 발명 제목",
        abstract="테스트 요약",
        background="테스트 배경",
        problem_statement="테스트 과제",
        solution="테스트 해결 수단",
        claims=["청구항 1", "청구항 2"],
        effects="테스트 효과",
    )


def _make_mock_triz() -> TRIZPrinciple:
    return TRIZPrinciple(
        number=1,
        name_en="Segmentation",
        name_ko="분할",
        description="Divide an object into independent parts",
        matching_score=0.85,
    )


def _make_mock_similar_patent() -> SimilarPatent:
    return SimilarPatent(
        title="선행 특허 제목",
        abstract="선행 특허 요약",
        application_number="10-2024-0001234",
        similarity_score=0.42,
    )


def _parse_sse_lines(raw: str) -> list[dict]:
    """Parse raw SSE text into a list of {event, data} dicts.

    Handles both ``\\r\\n`` (standard SSE) and ``\\n`` line endings.
    """
    events: list[dict] = []
    current_event: str | None = None
    current_data: str | None = None

    # Normalize line endings: replace \r\n with \n, then split
    for line in raw.replace("\r\n", "\n").split("\n"):
        if line.startswith("event:"):
            current_event = line[len("event:") :].strip()
        elif line.startswith("data:"):
            current_data = line[len("data:") :].strip()
        elif line == "":
            # Blank line = end of SSE message
            if current_event is not None and current_data is not None:
                events.append({"event": current_event, "data": current_data})
            current_event = None
            current_data = None

    # Handle trailing message without final blank line
    if current_event is not None and current_data is not None:
        events.append({"event": current_event, "data": current_data})

    return events


class MockPipeline:
    """Mock pipeline whose .stream() yields pre-defined events.

    Parameters
    ----------
    events : list[dict[str, dict]]
        Each item maps a node name to a partial state dict, mimicking
        what LangGraph astream yields.
    raise_after : int | None
        If set, raise RuntimeError after yielding this many events.
    """

    def __init__(
        self,
        events: list[dict[str, dict]],
        raise_after: int | None = None,
    ):
        self._events = events
        self._raise_after = raise_after

    async def stream(self, initial_state):
        for idx, event in enumerate(self._events):
            if self._raise_after is not None and idx >= self._raise_after:
                raise RuntimeError("Simulated pipeline failure")
            yield event


def _make_happy_path_events() -> list[dict[str, dict]]:
    """Return a realistic sequence of node events for the happy path."""
    triz = _make_mock_triz()
    similar = _make_mock_similar_patent()
    draft = _make_mock_draft()

    return [
        {
            "classify_triz": {
                "triz_principles": [triz],
                "current_step": "classify_triz",
                "reasoning_trace": ["[TRIZ 분류] 1개 원리 선정"],
            }
        },
        {
            "search_internal": {
                "similar_patents": [similar],
                "max_similarity_score": 0.42,
                "current_step": "search_internal",
                "reasoning_trace": [
                    "[TRIZ 분류] 1개 원리 선정",
                    "[내부 검색] 1건 검색, 최대 유사도: 42.0%",
                ],
            }
        },
        {
            "evaluate_context": {
                "context_sufficient": True,
                "current_step": "evaluate_context",
                "reasoning_trace": [
                    "[TRIZ 분류] 1개 원리 선정",
                    "[내부 검색] 1건 검색, 최대 유사도: 42.0%",
                    "[CRAG 평가] 컨텍스트 충분",
                ],
            }
        },
        {
            "generate_idea": {
                "current_idea": "테스트 아이디어",
                "current_step": "generate_idea",
                "reasoning_trace": [
                    "[TRIZ 분류] 1개 원리 선정",
                    "[내부 검색] 1건 검색, 최대 유사도: 42.0%",
                    "[CRAG 평가] 컨텍스트 충분",
                    "[아이디어 생성] TRIZ 원리 #1 분할(Segmentation) 적용",
                ],
            }
        },
        {
            "evaluate_novelty": {
                "novelty_score": 0.78,
                "novelty_reasoning": "충분히 독창적",
                "current_step": "evaluate_novelty",
                "reasoning_trace": [
                    "[TRIZ 분류] 1개 원리 선정",
                    "[내부 검색] 1건 검색, 최대 유사도: 42.0%",
                    "[CRAG 평가] 컨텍스트 충분",
                    "[아이디어 생성] TRIZ 원리 #1 분할(Segmentation) 적용",
                    "[신규성 평가] 점수: 78.0% → 독창적",
                ],
            }
        },
        {
            "draft_patent": {
                "final_idea": "테스트 아이디어",
                "patent_draft": draft,
                "docx_path": "data/drafts/test-draft-001.docx",
                "current_step": "draft_patent",
                "reasoning_trace": [
                    "[TRIZ 분류] 1개 원리 선정",
                    "[내부 검색] 1건 검색, 최대 유사도: 42.0%",
                    "[CRAG 평가] 컨텍스트 충분",
                    "[아이디어 생성] TRIZ 원리 #1 분할(Segmentation) 적용",
                    "[신규성 평가] 점수: 78.0% → 독창적",
                    "[완료] 특허 명세서 초안 생성",
                ],
            }
        },
    ]


# ── Tests ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_sse_happy_path():
    """Mock pipeline yields step events and a final done event."""
    mock = MockPipeline(events=_make_happy_path_events())
    app.dependency_overrides[get_pipeline] = lambda: mock

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/patent/generate/stream",
                json={"problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다"},
            )

        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" in content_type

        events = _parse_sse_lines(response.text)

        # Separate step events and done event
        step_events = [e for e in events if e["event"] == "step"]
        done_events = [e for e in events if e["event"] == "done"]
        error_events = [e for e in events if e["event"] == "error"]

        assert len(step_events) == 6
        assert len(done_events) == 1
        assert len(error_events) == 0

        # Verify the first step event matches the first node
        first_step_data = json.loads(step_events[0]["data"])
        assert first_step_data["step"] == "classify_triz"
        assert "state" in first_step_data

        # Verify each step event has the correct format
        for step_event in step_events:
            data = json.loads(step_event["data"])
            assert "step" in data
            assert isinstance(data["step"], str)
            assert "state" in data
            assert isinstance(data["state"], dict)

        # Verify the done event contains required fields
        done_data = json.loads(done_events[0]["data"])
        assert "patent_draft" in done_data
        assert done_data["patent_draft"] is not None
        assert done_data["patent_draft"]["title"] == "테스트 발명 제목"
        assert "triz_principles" in done_data
        assert len(done_data["triz_principles"]) == 1
        assert "similar_patents" in done_data
        assert len(done_data["similar_patents"]) == 1
        assert "reasoning_trace" in done_data
        assert len(done_data["reasoning_trace"]) > 0
        assert "novelty_score" in done_data
        assert done_data["novelty_score"] == 0.78
        assert "threshold" in done_data
        assert done_data["threshold"] is not None
        assert "draft_id" in done_data
        assert done_data["draft_id"] == "test-draft-001"
        assert "docx_download_url" in done_data

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sse_empty_input_validation():
    """Empty problem_description returns 422 validation error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/patent/generate/stream",
            json={"problem_description": ""},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_sse_mid_stream_pipeline_failure():
    """Pipeline raises RuntimeError after 2 events; error event is emitted, no done event."""
    events = _make_happy_path_events()
    mock = MockPipeline(events=events, raise_after=2)
    app.dependency_overrides[get_pipeline] = lambda: mock

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/patent/generate/stream",
                json={"problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다"},
            )

        assert response.status_code == 200

        events_parsed = _parse_sse_lines(response.text)

        step_events = [e for e in events_parsed if e["event"] == "step"]
        done_events = [e for e in events_parsed if e["event"] == "done"]
        error_events = [e for e in events_parsed if e["event"] == "error"]

        # Exactly 2 step events should have been yielded before the error
        assert len(step_events) == 2

        # No done event should be emitted
        assert len(done_events) == 0

        # An error event should be present
        assert len(error_events) == 1

        error_data = json.loads(error_events[0]["data"])
        assert "message" in error_data
        assert "Simulated pipeline failure" in error_data["message"]
        assert "step" in error_data

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sse_cors_headers():
    """SSE response includes Access-Control-Allow-Origin for allowed origin."""
    mock = MockPipeline(events=_make_happy_path_events())
    app.dependency_overrides[get_pipeline] = lambda: mock

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/patent/generate/stream",
                json={"problem_description": "발열은 줄이고 싶지만 두께는 얇아야 한다"},
                headers={"Origin": "http://localhost:3000"},
            )

        assert response.status_code == 200
        cors_header = response.headers.get("access-control-allow-origin")
        assert cors_header == "http://localhost:3000"

    finally:
        app.dependency_overrides.clear()
