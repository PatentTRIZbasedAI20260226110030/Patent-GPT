"""Tests for conversation memory service and session endpoints."""

import time

from fastapi.testclient import TestClient

from app.models.session import ConversationTurn, SessionHistory, SessionStore


class TestConversationTurn:
    def test_creation(self):
        turn = ConversationTurn(role="user", content="배터리 문제")
        assert turn.role == "user"
        assert turn.content == "배터리 문제"
        assert turn.timestamp > 0


class TestSessionHistory:
    def test_add_turn(self):
        session = SessionHistory(session_id="test-1")
        session.add_turn("user", "문제 설명")
        session.add_turn("assistant", "해결책")
        assert len(session.turns) == 2
        assert session.turns[0].role == "user"
        assert session.turns[1].role == "assistant"

    def test_format_for_prompt_empty(self):
        session = SessionHistory(session_id="test-1")
        assert session.format_for_prompt() == ""

    def test_format_for_prompt_with_turns(self):
        session = SessionHistory(session_id="test-1")
        session.add_turn("user", "배터리 과열")
        session.add_turn("assistant", "방열판 설계")
        result = session.format_for_prompt()
        assert "[사용자] 배터리 과열" in result
        assert "[시스템] 방열판 설계" in result

    def test_format_for_prompt_truncates(self):
        session = SessionHistory(session_id="test-1")
        for i in range(10):
            session.add_turn("user", f"turn {i}")
        result = session.format_for_prompt(max_turns=3)
        assert "turn 7" in result
        assert "turn 9" in result
        assert "turn 0" not in result


class TestSessionStore:
    def test_create_and_get(self):
        store = SessionStore()
        store.create("s1")
        session = store.get("s1")
        assert session is not None
        assert session.session_id == "s1"

    def test_get_nonexistent(self):
        store = SessionStore()
        assert store.get("missing") is None

    def test_get_or_create(self):
        store = SessionStore()
        s1 = store.get_or_create("s1")
        s1.add_turn("user", "test")
        s2 = store.get_or_create("s1")
        assert len(s2.turns) == 1

    def test_delete(self):
        store = SessionStore()
        store.create("s1")
        assert store.delete("s1") is True
        assert store.get("s1") is None
        assert store.delete("s1") is False

    def test_lru_eviction(self):
        store = SessionStore(max_sessions=2)
        store.create("s1")
        store.create("s2")
        store.create("s3")
        assert store.get("s1") is None
        assert store.get("s2") is not None
        assert store.get("s3") is not None

    def test_ttl_eviction(self):
        store = SessionStore(ttl_seconds=0)
        session = store.create("s1")
        session.created_at = time.time() - 1
        assert store.get("s1") is None

    def test_len(self):
        store = SessionStore()
        assert len(store) == 0
        store.create("s1")
        assert len(store) == 1


class TestSessionEndpoints:
    def _get_client(self):
        from app.main import app

        return TestClient(app)

    def test_get_session_not_found(self):
        client = self._get_client()
        resp = client.get("/api/v1/patent/session/nonexistent/history")
        assert resp.status_code == 404

    def test_delete_session_not_found(self):
        client = self._get_client()
        resp = client.delete("/api/v1/patent/session/nonexistent")
        assert resp.status_code == 404


class TestGenerateResponseIncludesSessionId:
    def test_response_with_session_id(self):
        from app.api.schemas.response import PatentGenerateResponse
        from app.models.patent_draft import PatentDraft

        draft = PatentDraft(
            title="테스트",
            abstract="요약",
            background="배경",
            problem_statement="과제",
            solution="해결",
            claims=["청구항1"],
            effects="효과",
        )
        resp = PatentGenerateResponse(
            patent_draft=draft,
            triz_principles=[],
            similar_patents=[],
            reasoning_trace=[],
            session_id="abc-123",
        )
        assert resp.session_id == "abc-123"

    def test_response_without_session_id(self):
        from app.api.schemas.response import PatentGenerateResponse
        from app.models.patent_draft import PatentDraft

        draft = PatentDraft(
            title="테스트",
            abstract="요약",
            background="배경",
            problem_statement="과제",
            solution="해결",
            claims=["청구항1"],
            effects="효과",
        )
        resp = PatentGenerateResponse(
            patent_draft=draft,
            triz_principles=[],
            similar_patents=[],
            reasoning_trace=[],
        )
        assert resp.session_id is None
