"""Tests for RAGAS evaluation models and endpoint."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.models.evaluation import EvaluationResult


class TestEvaluationResultModel:
    """Test EvaluationResult Pydantic model."""

    def test_valid_result(self):
        result = EvaluationResult(
            faithfulness=0.85,
            answer_relevancy=0.90,
            context_recall=0.75,
            passed=True,
        )
        assert result.faithfulness == 0.85
        assert result.passed is True

    def test_failed_result(self):
        result = EvaluationResult(
            faithfulness=0.5,
            answer_relevancy=0.6,
            context_recall=0.4,
            passed=False,
        )
        assert result.passed is False

    def test_serialization(self):
        result = EvaluationResult(
            faithfulness=0.85,
            answer_relevancy=0.90,
            context_recall=0.75,
            passed=True,
        )
        data = result.model_dump()
        assert data["faithfulness"] == 0.85
        assert data["passed"] is True
        assert set(data.keys()) == {
            "faithfulness",
            "answer_relevancy",
            "context_recall",
            "passed",
        }


class TestEvaluateEndpoint:
    """Test POST /api/v1/patent/evaluate endpoint."""

    def _get_client(self):
        from app.main import app

        return TestClient(app)

    @patch("app.api.routes.patent.evaluate_pipeline_output")
    def test_evaluate_returns_result(self, mock_eval):
        mock_eval.return_value = EvaluationResult(
            faithfulness=0.9,
            answer_relevancy=0.85,
            context_recall=0.8,
            passed=True,
        )
        client = self._get_client()
        resp = client.post(
            "/api/v1/patent/evaluate",
            json={
                "user_problem": "배터리 과열 문제",
                "generated_idea": "방열판을 추가한 설계",
                "retrieved_contexts": ["선행특허 A 요약"],
                "reference": "",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["faithfulness"] == 0.9
        assert data["passed"] is True

    def test_evaluate_rejects_empty_problem(self):
        client = self._get_client()
        resp = client.post(
            "/api/v1/patent/evaluate",
            json={
                "user_problem": "",
                "generated_idea": "something",
            },
        )
        assert resp.status_code == 422

    def test_evaluate_rejects_empty_idea(self):
        client = self._get_client()
        resp = client.post(
            "/api/v1/patent/evaluate",
            json={
                "user_problem": "문제",
                "generated_idea": "",
            },
        )
        assert resp.status_code == 422


class TestGenerateResponseIncludesEvaluation:
    """Test that PatentGenerateResponse accepts optional evaluation."""

    def test_response_with_evaluation(self):
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
        evaluation = EvaluationResult(
            faithfulness=0.9,
            answer_relevancy=0.85,
            context_recall=0.8,
            passed=True,
        )
        resp = PatentGenerateResponse(
            patent_draft=draft,
            triz_principles=[],
            similar_patents=[],
            reasoning_trace=[],
            evaluation=evaluation,
        )
        assert resp.evaluation is not None
        assert resp.evaluation.passed is True

    def test_response_without_evaluation(self):
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
        assert resp.evaluation is None


class TestEvaluationConfig:
    """Test evaluation-related config fields."""

    def test_default_threshold(self):
        from app.config import Settings

        s = Settings()
        assert s.FAITHFULNESS_THRESHOLD == 0.8

    def test_default_auto_evaluation_off(self):
        from app.config import Settings

        s = Settings()
        assert s.ENABLE_AUTO_EVALUATION is False
