"""ML-based TRIZ classifier using a trained model (XGBoost + TF-IDF)."""

import logging
from pathlib import Path

import joblib

from app.models.triz import TRIZPrinciple, load_triz_principles

logger = logging.getLogger(__name__)


class MLTrizClassifier:
    """Predict TRIZ principles from problem text using a trained ML model."""

    def __init__(self, model_path: str):
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(
                f"ML model not found at {model_path}. "
                "Train with: python scripts/train_triz_classifier.py"
            )
        artifact = joblib.load(path)
        self._vectorizer = artifact["vectorizer"]
        self._model = artifact["model"]
        self._label_names = artifact.get("label_names", [])
        self._principles = {p.number: p for p in load_triz_principles()}

    def predict(self, text: str, top_k: int = 3) -> list[TRIZPrinciple]:
        """Predict top-k TRIZ principles for a problem description."""
        features = self._vectorizer.transform([text])
        probas = self._model.predict_proba(features)[0]

        # Get top-k class indices by probability
        top_indices = probas.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            principle_num = int(self._label_names[idx])
            score = float(probas[idx])
            p = self._principles.get(principle_num)
            if p:
                results.append(
                    TRIZPrinciple(
                        number=p.number,
                        name_en=p.name_en,
                        name_ko=p.name_ko,
                        description=p.description,
                        matching_score=round(score, 4),
                    )
                )
        return results
