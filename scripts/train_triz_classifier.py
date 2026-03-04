"""Train a TF-IDF + XGBoost TRIZ classifier from labeled patent data.

Usage examples:
    python scripts/train_triz_classifier.py --data data/training/triz_labels.jsonl
    python scripts/train_triz_classifier.py \
        --data data/training/triz_labels.ko.jsonl \
        --output data/models/triz_classifier_ko.joblib \
        --metrics-output data/models/triz_classifier_ko.metrics.json

Input format (JSONL):
    {"text": "problem description in Korean", "labels": [1, 15, 35]}

Primary output:
    data/models/triz_classifier.joblib
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any

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


def calculate_topk_recall(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    top_k: int,
) -> tuple[float, int, int]:
    """Compute production-style top-k recall for multi-label predictions.

    Args:
        y_true: Multi-hot ground truth labels.
        y_proba: Per-label probabilities from the trained model.
        top_k: Number of labels selected per sample.

    Returns:
        Tuple of (recall, hits, total_true_labels).
    """
    topk_hits = 0
    topk_total = 0
    for i in range(len(y_proba)):
        true_labels = set(np.where(y_true[i] == 1)[0])
        pred_top = set(np.argsort(y_proba[i])[-top_k:])
        topk_hits += len(true_labels & pred_top)
        topk_total += len(true_labels)
    topk_recall = topk_hits / topk_total if topk_total else 0.0
    return float(topk_recall), int(topk_hits), int(topk_total)


def train(
    data_path: Path,
    output_path: Path,
    *,
    test_size: float = 0.2,
    random_state: int = 42,
    tfidf_max_features: int = 10000,
    tfidf_ngram_max: int = 2,
    xgb_n_estimators: int = 400,
    xgb_max_depth: int = 10,
    xgb_learning_rate: float = 0.1,
    xgb_scale_pos_weight: float = 5.0,
    xgb_min_child_weight: float = 2.0,
    xgb_subsample: float = 0.8,
    xgb_colsample_bytree: float = 0.8,
    top_k: int = 5,
    print_classification_report: bool = True,
) -> dict[str, Any]:
    """Train and evaluate TRIZ multi-label classifier.

    Args:
        data_path: Input JSONL data path.
        output_path: Joblib artifact path.
        test_size: Validation split ratio.
        random_state: Random seed for split/model.
        tfidf_max_features: Max vocabulary size for TF-IDF.
        tfidf_ngram_max: Upper bound for ngram_range.
        xgb_n_estimators: XGBoost n_estimators.
        xgb_max_depth: XGBoost max_depth.
        xgb_learning_rate: XGBoost learning_rate.
        xgb_scale_pos_weight: XGBoost scale_pos_weight.
        xgb_min_child_weight: XGBoost min_child_weight.
        xgb_subsample: XGBoost subsample.
        xgb_colsample_bytree: XGBoost colsample_bytree.
        top_k: Top-k for production-style recall metric.
        print_classification_report: Whether to log class report.

    Returns:
        Dictionary with artifact and summary metrics.
    """
    started_at = time.perf_counter()
    logger.info("Loading training data from %s", data_path)
    texts, y, label_names = load_training_data(data_path)
    logger.info("Loaded %d samples, %d unique labels", len(texts), len(label_names))

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        y,
        test_size=test_size,
        random_state=random_state,
    )

    vectorizer = TfidfVectorizer(
        max_features=tfidf_max_features,
        ngram_range=(1, tfidf_ngram_max),
        sublinear_tf=True,
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    model = OneVsRestClassifier(
        XGBClassifier(
            n_estimators=xgb_n_estimators,
            max_depth=xgb_max_depth,
            learning_rate=xgb_learning_rate,
            eval_metric="logloss",
            scale_pos_weight=xgb_scale_pos_weight,
            min_child_weight=xgb_min_child_weight,
            subsample=xgb_subsample,
            colsample_bytree=xgb_colsample_bytree,
            random_state=random_state,
        )
    )
    logger.info("Training XGBoost classifier...")
    model.fit(X_train_tfidf, y_train)

    # --- Hard-threshold evaluation (standard) ---
    y_pred = model.predict(X_test_tfidf)
    f1_micro = f1_score(y_test, y_pred, average="micro")
    f1_macro = f1_score(y_test, y_pred, average="macro")

    logger.info("F1 micro: %.4f, F1 macro: %.4f", f1_micro, f1_macro)
    if print_classification_report:
        logger.info("\n%s", classification_report(y_test, y_pred, zero_division=0))

    # --- Top-k evaluation (matches production inference) ---
    # In production, MLTrizClassifier.predict() uses predict_proba + top-k.
    # Evaluate with the same approach to get a realistic accuracy metric.
    y_proba = model.predict_proba(X_test_tfidf)
    topk_recall, topk_hits, topk_total = calculate_topk_recall(
        y_true=y_test,
        y_proba=y_proba,
        top_k=top_k,
    )
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
    elapsed_seconds = time.perf_counter() - started_at
    training_config = {
        "test_size": test_size,
        "random_state": random_state,
        "tfidf_max_features": tfidf_max_features,
        "tfidf_ngram_max": tfidf_ngram_max,
        "xgb_n_estimators": xgb_n_estimators,
        "xgb_max_depth": xgb_max_depth,
        "xgb_learning_rate": xgb_learning_rate,
        "xgb_scale_pos_weight": xgb_scale_pos_weight,
        "xgb_min_child_weight": xgb_min_child_weight,
        "xgb_subsample": xgb_subsample,
        "xgb_colsample_bytree": xgb_colsample_bytree,
        "top_k": top_k,
    }
    artifact = {
        "vectorizer": vectorizer,
        "model": model,
        "label_names": [str(lbl) for lbl in label_names],
        "f1_micro": float(f1_micro),
        "f1_macro": float(f1_macro),
        "topk_recall": float(topk_recall),
        "topk_hits": int(topk_hits),
        "topk_total": int(topk_total),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "elapsed_seconds": float(elapsed_seconds),
        "config": training_config,
    }
    joblib.dump(artifact, output_path)
    logger.info("Model saved to %s", output_path)
    return artifact


def main() -> None:
    """Parse CLI arguments and run training."""
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
    parser.add_argument("--metrics-output", type=Path, default=None)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--tfidf-max-features", type=int, default=10000)
    parser.add_argument("--tfidf-ngram-max", type=int, default=2)
    parser.add_argument("--xgb-n-estimators", type=int, default=400)
    parser.add_argument("--xgb-max-depth", type=int, default=10)
    parser.add_argument("--xgb-learning-rate", type=float, default=0.1)
    parser.add_argument("--xgb-scale-pos-weight", type=float, default=5.0)
    parser.add_argument("--xgb-min-child-weight", type=float, default=2.0)
    parser.add_argument("--xgb-subsample", type=float, default=0.8)
    parser.add_argument("--xgb-colsample-bytree", type=float, default=0.8)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--skip-classification-report",
        action="store_true",
        help="Disable verbose per-class report logging.",
    )
    args = parser.parse_args()

    if not args.data.exists():
        logger.error(
            "Training data not found at %s. "
            "Create JSONL with {text, labels} records first.",
            args.data,
        )
        return

    metrics = train(
        data_path=args.data,
        output_path=args.output,
        test_size=args.test_size,
        random_state=args.random_state,
        tfidf_max_features=args.tfidf_max_features,
        tfidf_ngram_max=args.tfidf_ngram_max,
        xgb_n_estimators=args.xgb_n_estimators,
        xgb_max_depth=args.xgb_max_depth,
        xgb_learning_rate=args.xgb_learning_rate,
        xgb_scale_pos_weight=args.xgb_scale_pos_weight,
        xgb_min_child_weight=args.xgb_min_child_weight,
        xgb_subsample=args.xgb_subsample,
        xgb_colsample_bytree=args.xgb_colsample_bytree,
        top_k=args.top_k,
        print_classification_report=not args.skip_classification_report,
    )

    if args.metrics_output is not None:
        args.metrics_output.parent.mkdir(parents=True, exist_ok=True)
        summary = {
            "data_path": str(args.data),
            "output_path": str(args.output),
            "f1_micro": metrics["f1_micro"],
            "f1_macro": metrics["f1_macro"],
            "topk_recall": metrics["topk_recall"],
            "topk_hits": metrics["topk_hits"],
            "topk_total": metrics["topk_total"],
            "train_samples": metrics["train_samples"],
            "test_samples": metrics["test_samples"],
            "elapsed_seconds": metrics["elapsed_seconds"],
            "config": metrics["config"],
        }
        args.metrics_output.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Metrics saved to %s", args.metrics_output)


if __name__ == "__main__":
    main()
