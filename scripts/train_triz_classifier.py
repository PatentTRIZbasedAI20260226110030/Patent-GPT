"""Train a TF-IDF + XGBoost TRIZ classifier from labeled patent data.

Usage:
    python scripts/train_triz_classifier.py [--data data/training/triz_labels.jsonl]

Input format (JSONL):
    {"text": "problem description in Korean", "labels": [1, 15, 35]}

Output:
    data/models/triz_classifier.joblib
"""

import argparse
import json
import logging
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from xgboost import XGBClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
MODEL_DIR = DATA_DIR / "models"


def load_training_data(path: Path) -> tuple[list[str], np.ndarray]:
    """Load JSONL training data and return texts + multi-hot label matrix."""
    texts = []
    label_sets = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            texts.append(record["text"])
            label_sets.append(record["labels"])

    # Build multi-hot encoding for 40 TRIZ principles
    all_labels = sorted({lbl for ls in label_sets for lbl in ls})
    label_to_idx = {lbl: idx for idx, lbl in enumerate(all_labels)}
    y = np.zeros((len(texts), len(all_labels)), dtype=int)
    for i, ls in enumerate(label_sets):
        for lbl in ls:
            y[i, label_to_idx[lbl]] = 1

    return texts, y, all_labels


def train(data_path: Path, output_path: Path) -> None:
    logger.info("Loading training data from %s", data_path)
    texts, y, label_names = load_training_data(data_path)
    logger.info("Loaded %d samples, %d unique labels", len(texts), len(label_names))

    X_train, X_test, y_train, y_test = train_test_split(
        texts, y, test_size=0.2, random_state=42
    )

    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    model = OneVsRestClassifier(
        XGBClassifier(
            n_estimators=400,
            max_depth=10,
            learning_rate=0.1,
            eval_metric="logloss",
            scale_pos_weight=5,
            min_child_weight=2,
            subsample=0.8,
            colsample_bytree=0.8,
        )
    )
    logger.info("Training XGBoost classifier...")
    model.fit(X_train_tfidf, y_train)

    # --- Hard-threshold evaluation (standard) ---
    y_pred = model.predict(X_test_tfidf)
    f1_micro = f1_score(y_test, y_pred, average="micro")
    f1_macro = f1_score(y_test, y_pred, average="macro")

    logger.info("F1 micro: %.4f, F1 macro: %.4f", f1_micro, f1_macro)
    logger.info("\n%s", classification_report(y_test, y_pred, zero_division=0))

    # --- Top-k evaluation (matches production inference) ---
    # In production, MLTrizClassifier.predict() uses predict_proba + top-k.
    # Evaluate with the same approach to get a realistic accuracy metric.
    y_proba = model.predict_proba(X_test_tfidf)
    top_k = 5
    topk_hits = 0
    topk_total = 0
    for i in range(len(y_proba)):
        true_labels = set(np.where(y_test[i] == 1)[0])
        pred_top = set(np.argsort(y_proba[i])[-top_k:])
        topk_hits += len(true_labels & pred_top)
        topk_total += len(true_labels)
    topk_recall = topk_hits / topk_total if topk_total else 0
    logger.info(
        "Top-%d recall (production-style): %.4f (%d/%d)",
        top_k, topk_recall, topk_hits, topk_total,
    )

    if f1_micro < 0.75:
        logger.warning(
            "F1 micro (%.4f) is below 0.75 threshold. "
            "Model saved but NOT recommended for production use.",
            f1_micro,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "vectorizer": vectorizer,
        "model": model,
        "label_names": [str(lbl) for lbl in label_names],
        "f1_micro": f1_micro,
        "f1_macro": f1_macro,
    }
    joblib.dump(artifact, output_path)
    logger.info("Model saved to %s", output_path)


def main():
    parser = argparse.ArgumentParser(description="Train TRIZ classifier")
    parser.add_argument(
        "--data",
        type=Path,
        default=DATA_DIR / "training" / "triz_labels.jsonl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=MODEL_DIR / "triz_classifier.joblib",
    )
    args = parser.parse_args()

    if not args.data.exists():
        logger.error(
            "Training data not found at %s. "
            "Create JSONL with {text, labels} records first.",
            args.data,
        )
        return

    train(args.data, args.output)


if __name__ == "__main__":
    main()
