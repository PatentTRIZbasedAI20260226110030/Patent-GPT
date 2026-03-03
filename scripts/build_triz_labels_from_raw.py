"""Build TRIZ multi-label training data from raw TRIZ documents.

This script creates `data/training/triz_labels.jsonl` with records in the format:
    {"text": "Korean problem description", "labels": [1, 15, 35]}

Pipeline:
1. Extract Korean problem-like sentences from PDFs in the raw folder.
2. Parse TRIZ matrix + contradiction CSV files.
3. Generate labeled samples by pairing extracted sentences with contradiction rows.
4. Optionally validate a subset with the existing LLM TRIZ classifier (teacher).
5. Enforce label coverage for all 40 TRIZ principles.
6. Save JSONL and a stats JSON report.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import random
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

KOREAN_RE = re.compile(r"[가-힣]")
PROBLEM_LIKE_RE = re.compile(
    r"(해야|필요|문제|개선|증가|감소|악화|저하|향상|유지|부족|어렵|위해|하지만|그러나)"
)
SPLIT_RE = re.compile(r"[.!?]\s+|\n+")


@dataclass
class MatrixRow:
    """TRIZ matrix row mapped to contradiction pair and principles."""

    improving: int
    worsening: int
    labels: list[int]


def clean_text(text: str) -> str:
    """Normalize whitespace and remove obvious page artifacts."""

    normalized = re.sub(r"\s+", " ", text).strip()
    normalized = re.sub(r"--\s*\d+\s*of\s*\d+\s*--", " ", normalized, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", normalized).strip()


def is_candidate_sentence(sentence: str) -> bool:
    """Return True if sentence looks like a Korean problem statement."""

    if not sentence or len(sentence) < 15 or len(sentence) > 220:
        return False
    if not KOREAN_RE.search(sentence):
        return False
    if re.fullmatch(r"[0-9\s\-/.,()]+", sentence):
        return False
    return bool(PROBLEM_LIKE_RE.search(sentence))


def extract_sentences_from_pdf(pdf_path: Path) -> list[str]:
    """Extract Korean candidate sentences from a single PDF file."""

    from pypdf import PdfReader

    results: list[str] = []
    reader = PdfReader(str(pdf_path))
    for page in reader.pages:
        text = clean_text(page.extract_text() or "")
        if not text:
            continue
        for raw in SPLIT_RE.split(text):
            sentence = clean_text(raw)
            if is_candidate_sentence(sentence):
                results.append(sentence)
    return results


def parse_int_list(text: str) -> list[int]:
    """Parse principle list strings like '3, 19, 35, 40'."""

    values: list[int] = []
    for chunk in text.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.isdigit():
            value = int(chunk)
            if 1 <= value <= 40:
                values.append(value)
    return sorted(set(values))


def load_parameters(path: Path) -> dict[int, str]:
    """Load TRIZ parameter names indexed by 1-based id."""

    with path.open(encoding="utf-8-sig") as f:
        rows = [clean_text(line) for line in f if clean_text(line)]
    # CSV is one-column (header + values)
    values = rows[1:]
    return {idx + 1: name for idx, name in enumerate(values)}


def load_matrix_rows(contradictions_csv: Path, matrix_csv: Path) -> list[MatrixRow]:
    """Load matrix rows aligned by row order from contradiction + matrix CSV files."""

    contradiction_pairs: list[tuple[int, int]] = []
    with contradictions_csv.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pair_text = (row.get("Improving,worsening") or "").replace('"', "").strip()
            pair_parts = [p.strip() for p in pair_text.split(",") if p.strip().isdigit()]
            if len(pair_parts) != 2:
                continue
            contradiction_pairs.append((int(pair_parts[0]), int(pair_parts[1])))

    matrix_labels: list[list[int]] = []
    with matrix_csv.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label_text = (row.get("Principles") or "").replace('"', "")
            labels = parse_int_list(label_text)
            matrix_labels.append(labels)

    rows: list[MatrixRow] = []
    for idx, pair in enumerate(contradiction_pairs):
        if idx >= len(matrix_labels):
            break
        labels = matrix_labels[idx]
        if labels:
            rows.append(MatrixRow(improving=pair[0], worsening=pair[1], labels=labels))
    return rows


def build_initial_samples(
    sentences: list[str],
    rows: list[MatrixRow],
    parameter_names: dict[int, str],
    target_size: int,
    seed: int,
) -> list[dict[str, Any]]:
    """Build initial labeled samples by cycling through extracted sentences + matrix rows."""

    rng = random.Random(seed)
    shuffled_sentences = list(dict.fromkeys(sentences))  # dedupe preserving order
    rng.shuffle(shuffled_sentences)
    shuffled_rows = rows[:]
    rng.shuffle(shuffled_rows)

    samples: list[dict[str, Any]] = []
    for idx in range(target_size):
        base = shuffled_sentences[idx % len(shuffled_sentences)]
        row = shuffled_rows[idx % len(shuffled_rows)]
        improving_name = parameter_names.get(row.improving, f"파라미터 {row.improving}")
        worsening_name = parameter_names.get(row.worsening, f"파라미터 {row.worsening}")
        text = (
            f"{base} 또한 {improving_name}은(는) 향상해야 하지만 "
            f"{worsening_name}의 악화는 방지해야 한다."
        )
        samples.append({"text": text, "labels": row.labels})
    return samples


def enforce_full_label_coverage(
    samples: list[dict[str, Any]],
    rows: list[MatrixRow],
    parameter_names: dict[int, str],
) -> None:
    """Ensure all labels 1..40 appear at least once by replacing head samples if needed."""

    all_labels = set(range(1, 41))
    present = {label for sample in samples for label in sample["labels"]}
    missing = sorted(all_labels - present)
    if not missing:
        return

    replace_idx = 0
    for label in missing:
        candidate = next((row for row in rows if label in row.labels), None)
        if not candidate or replace_idx >= len(samples):
            continue
        improving_name = parameter_names.get(candidate.improving, f"파라미터 {candidate.improving}")
        worsening_name = parameter_names.get(candidate.worsening, f"파라미터 {candidate.worsening}")
        base = samples[replace_idx]["text"].split(" 또한 ")[0]
        samples[replace_idx] = {
            "text": (
                f"{base} 또한 {improving_name}은(는) 향상해야 하지만 "
                f"{worsening_name}의 악화는 방지해야 한다."
            ),
            "labels": candidate.labels,
        }
        replace_idx += 1


async def validate_with_teacher(
    samples: list[dict[str, Any]],
    validate_count: int,
    technical_field: str,
) -> int:
    """Validate a subset with LLM teacher and relabel when there is no overlap."""

    if validate_count <= 0:
        return 0

    from app.config import Settings
    from app.services.triz_classifier import classify_triz

    settings = Settings()
    updated = 0

    for sample in samples[:validate_count]:
        predicted = await classify_triz(
            problem_description=sample["text"],
            technical_field=technical_field,
            settings=settings,
        )
        predicted_labels = [p.number for p in predicted if 1 <= p.number <= 40]
        if not predicted_labels:
            continue
        overlap = set(sample["labels"]) & set(predicted_labels)
        if not overlap:
            sample["labels"] = sorted(set(predicted_labels))
            updated += 1
    return updated


def compute_stats(samples: list[dict[str, Any]]) -> dict[str, Any]:
    """Build dataset statistics."""

    label_counter: Counter[int] = Counter()
    for sample in samples:
        for label in sample["labels"]:
            label_counter[label] += 1

    all_labels = set(range(1, 41))
    present_labels = set(label_counter.keys())
    return {
        "num_samples": len(samples),
        "unique_labels": len(present_labels),
        "missing_labels": sorted(all_labels - present_labels),
        "min_label_frequency": min(label_counter.values()) if label_counter else 0,
        "max_label_frequency": max(label_counter.values()) if label_counter else 0,
        "avg_labels_per_sample": (
            sum(len(sample["labels"]) for sample in samples) / len(samples) if samples else 0.0
        ),
        "label_frequencies": {str(k): label_counter[k] for k in sorted(label_counter)},
    }


def write_jsonl(path: Path, samples: list[dict[str, Any]]) -> None:
    """Write samples to JSONL file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for sample in samples:
            record = {"text": sample["text"], "labels": sorted(set(sample["labels"]))}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Build TRIZ labeled JSONL from raw documents")
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("TRIZ classificaion database (raw)"),
        help="Path to raw TRIZ folder",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/training/triz_labels.jsonl"),
        help="Output JSONL path",
    )
    parser.add_argument(
        "--target-size",
        type=int,
        default=500,
        help="Number of samples to generate",
    )
    parser.add_argument(
        "--teacher-validate",
        type=int,
        default=30,
        help="Number of leading samples to validate with LLM teacher",
    )
    parser.add_argument(
        "--technical-field",
        type=str,
        default="특허/기계/전자 일반",
        help="Technical field passed to teacher classifier",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


async def async_main() -> None:
    """Run the full dataset build pipeline."""

    args = parse_args()
    raw_dir = args.raw_dir

    pdf_paths = sorted(raw_dir.rglob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found in {raw_dir}")

    sentences: list[str] = []
    for pdf_path in pdf_paths:
        try:
            sentences.extend(extract_sentences_from_pdf(pdf_path))
        except (ValueError, OSError, RuntimeError):
            continue

    sentences = list(dict.fromkeys(sentences))
    if len(sentences) < 30:
        raise RuntimeError(
            "Not enough candidate sentences extracted from PDFs. "
            "Need at least 30 to build varied samples."
        )

    data_root = raw_dir / "triz-database-design-main" / "triz_data"
    parameter_path = data_root / "TRIZ_parameters.csv"
    contradictions_path = data_root / "TRIZ_contradictions.csv"
    matrix_path = data_root / "TRIZ_matrix.csv"

    parameter_names = load_parameters(parameter_path)
    rows = load_matrix_rows(contradictions_path, matrix_path)
    if not rows:
        raise RuntimeError("No usable matrix rows parsed from TRIZ CSV files.")

    samples = build_initial_samples(
        sentences=sentences,
        rows=rows,
        parameter_names=parameter_names,
        target_size=args.target_size,
        seed=args.seed,
    )

    teacher_updates = 0
    if args.teacher_validate > 0:
        try:
            teacher_updates = await validate_with_teacher(
                samples=samples,
                validate_count=min(args.teacher_validate, len(samples)),
                technical_field=args.technical_field,
            )
        except (ImportError, RuntimeError, ValueError, TypeError):
            teacher_updates = 0

    enforce_full_label_coverage(samples, rows, parameter_names)
    # Final safety filter for label range.
    for sample in samples:
        sample["labels"] = sorted({label for label in sample["labels"] if 1 <= label <= 40})
        if not sample["labels"]:
            sample["labels"] = [1]

    write_jsonl(args.output, samples)
    stats = compute_stats(samples)
    stats["source_pdf_count"] = len(pdf_paths)
    stats["candidate_sentence_count"] = len(sentences)
    stats["teacher_updated_samples"] = teacher_updates

    stats_path = args.output.parent / "triz_labels_stats.json"
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"\nSaved: {args.output}")
    print(f"Saved: {stats_path}")


if __name__ == "__main__":
    asyncio.run(async_main())
