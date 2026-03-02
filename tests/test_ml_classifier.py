"""Tests for ML TRIZ classifier and router config."""

from unittest.mock import MagicMock, patch

import pytest

from app.models.triz import TRIZPrinciple


class TestTrizRouterConfig:
    """Test TRIZ_ROUTER config flag."""

    def test_default_router_is_llm(self):
        from app.config import Settings

        s = Settings()
        assert s.TRIZ_ROUTER == "llm"

    def test_ml_model_path_default(self):
        from app.config import Settings

        s = Settings()
        assert s.ML_MODEL_PATH == "./data/models/triz_classifier.joblib"


class TestMLClassifierMissing:
    """Test ML classifier when model file is missing."""

    def test_raises_when_model_not_found(self):
        from app.services.ml_classifier import MLTrizClassifier

        with pytest.raises(FileNotFoundError, match="ML model not found"):
            MLTrizClassifier("/nonexistent/model.joblib")


class TestClassifyTrizRouter:
    """Test that classify_triz routes based on settings."""

    @patch("app.services.triz_classifier._classify_triz_llm")
    async def test_routes_to_llm_by_default(self, mock_llm):
        from app.config import Settings
        from app.services.triz_classifier import classify_triz

        mock_llm.return_value = [
            TRIZPrinciple(
                number=1, name_en="Segmentation",
                name_ko="분할", description="test",
            )
        ]
        settings = Settings()
        result = await classify_triz("문제", "전자", settings)
        mock_llm.assert_called_once()
        assert len(result) == 1

    @patch("app.services.triz_classifier._classify_triz_ml")
    async def test_routes_to_ml_when_configured(self, mock_ml):
        from app.config import Settings
        from app.services.triz_classifier import classify_triz

        mock_ml.return_value = [
            TRIZPrinciple(
                number=2, name_en="Taking out",
                name_ko="추출", description="test",
            )
        ]
        settings = Settings()
        settings.TRIZ_ROUTER = "ml"
        result = await classify_triz("문제", "전자", settings)
        mock_ml.assert_called_once()
        assert result[0].number == 2


class TestMLClassifierPredict:
    """Test MLTrizClassifier.predict with mocked model."""

    @patch("app.services.ml_classifier.joblib")
    @patch("app.services.ml_classifier.Path")
    def test_predict_returns_principles(self, mock_path_cls, mock_joblib):
        from app.services.ml_classifier import MLTrizClassifier

        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path_cls.return_value = mock_path

        mock_vectorizer = MagicMock()
        mock_vectorizer.transform.return_value = "features"

        import numpy as np

        mock_model = MagicMock()
        mock_model.predict_proba.return_value = [
            np.array([0.9, 0.1, 0.8])
        ]

        mock_joblib.load.return_value = {
            "vectorizer": mock_vectorizer,
            "model": mock_model,
            "label_names": ["1", "2", "3"],
        }

        classifier = MLTrizClassifier("/fake/model.joblib")
        results = classifier.predict("배터리 과열 문제", top_k=2)

        assert len(results) == 2
        assert results[0].number == 1
        assert results[0].matching_score == 0.9
        assert results[1].number == 3
