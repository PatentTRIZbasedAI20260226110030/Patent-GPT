"""Generate TRIZ ML training data from the contradiction matrix.

Reads the 39×38 contradiction matrix (1482 pairs) and generates
English problem descriptions with ground-truth TRIZ principle labels.

Usage:
    python scripts/build_triz_training_data.py

Input:
    TRIZ classificaion database (raw)/triz-database-design-main/triz_data/
        TRIZ_parameters.csv    — 39 engineering parameter names
        TRIZ_contradictions.csv — (improving, worsening) parameter pairs
        TRIZ_matrix.csv        — recommended TRIZ principles per pair

Output:
    data/training/triz_labels.jsonl       — training data
    data/training/triz_labels_stats.json  — dataset statistics
"""

import csv
import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "TRIZ classificaion database (raw)" / "triz-database-design-main" / "triz_data"
OUT_DIR = ROOT / "data" / "training"

# ---------------------------------------------------------------------------
# Sentence templates — each takes (improving, worsening) parameter names.
# Diverse phrasings so the TF-IDF vectorizer learns meaningful n-grams,
# not just a single template pattern.
# ---------------------------------------------------------------------------
TEMPLATES = [
    "Need to improve {imp} without degrading {wor}.",
    "The system requires better {imp} but {wor} must not get worse.",
    "Improve {imp} while maintaining acceptable {wor}.",
    "How to increase {imp} without negatively affecting {wor}.",
    "Design challenge: enhance {imp} but prevent deterioration of {wor}.",
    "{imp} should be maximized while keeping {wor} stable.",
    "Reduce trade-off between {imp} and {wor} in the design.",
    "The contradiction is that improving {imp} tends to worsen {wor}.",
    "Find a way to boost {imp} performance without sacrificing {wor}.",
    "Engineering problem: {imp} improvement causes {wor} degradation.",
    "We want higher {imp} but cannot tolerate lower {wor}.",
    "Optimize {imp} under the constraint that {wor} remains unchanged.",
]

# Additional domain-flavored templates for variety
DOMAIN_TEMPLATES = [
    "In this device, {imp} must increase but {wor} is already at its limit.",
    "The product needs better {imp}, however {wor} cannot be compromised.",
    "Users demand improved {imp} while {wor} stays within tolerance.",
    "The prototype fails because enhancing {imp} always degrades {wor}.",
    "Achieve superior {imp} in the mechanism without worsening {wor}.",
    "The technical barrier: {imp} and {wor} are inversely coupled.",
    "Improve the {imp} of the component while preserving its {wor}.",
    "The goal is to decouple {imp} from {wor} in the system.",
]

ALL_TEMPLATES = TEMPLATES + DOMAIN_TEMPLATES


def load_parameters(path: Path) -> dict[int, str]:
    """Load 39 engineering parameters. Returns {1: 'Weight of Moving Object', ...}."""
    params = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header "Parameters"
        for idx, row in enumerate(reader, start=1):
            params[idx] = row[0].strip()
    return params


def load_contradictions(path: Path) -> list[tuple[int, int]]:
    """Load contradiction pairs. Returns [(improving, worsening), ...]."""
    pairs = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            raw = row[0].strip().strip('"')
            imp, wor = raw.split(",")
            pairs.append((int(imp), int(wor)))
    return pairs


def load_matrix(path: Path) -> list[list[int]]:
    """Load principle recommendations. Returns [[3,19,35,40], [17,15,8,35], ...]."""
    principles_list = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header "Contradiction,Principles"
        for row in reader:
            raw = row[1].strip().strip('"')
            # Handle malformed entries like "2,, 26, 19, 3"
            nums = [int(x.strip()) for x in raw.split(",") if x.strip()]
            principles_list.append(nums)
    return principles_list


def generate_samples(
    params: dict[int, str],
    pairs: list[tuple[int, int]],
    principles_list: list[list[int]],
    templates_per_pair: int = 3,
    seed: int = 42,
) -> list[dict]:
    """Generate training samples from contradiction matrix data."""
    rng = random.Random(seed)
    samples = []

    for (imp_id, wor_id), principles in zip(pairs, principles_list):
        imp_name = params.get(imp_id, f"Parameter {imp_id}")
        wor_name = params.get(wor_id, f"Parameter {wor_id}")

        # Clean up multi-space parameter names
        imp_name = " ".join(imp_name.split())
        wor_name = " ".join(wor_name.split())

        # Pick random templates for this pair
        chosen = rng.sample(ALL_TEMPLATES, min(templates_per_pair, len(ALL_TEMPLATES)))

        for template in chosen:
            text = template.format(imp=imp_name, wor=wor_name)
            samples.append({"text": text, "labels": sorted(set(principles))})

    rng.shuffle(samples)
    return samples


def compute_stats(samples: list[dict]) -> dict:
    """Compute dataset statistics."""
    label_counter: Counter = Counter()
    labels_per_sample = []

    for s in samples:
        for lbl in s["labels"]:
            label_counter[lbl] += 1
        labels_per_sample.append(len(s["labels"]))

    all_expected = set(range(1, 41))
    present = set(label_counter.keys())
    missing = sorted(all_expected - present)

    return {
        "num_samples": len(samples),
        "unique_labels": len(present),
        "missing_labels": missing,
        "min_label_frequency": min(label_counter.values()) if label_counter else 0,
        "max_label_frequency": max(label_counter.values()) if label_counter else 0,
        "avg_labels_per_sample": round(sum(labels_per_sample) / len(samples), 2),
        "label_frequencies": {str(k): v for k, v in sorted(label_counter.items())},
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading raw TRIZ data...")
    params = load_parameters(RAW_DIR / "TRIZ_parameters.csv")
    pairs = load_contradictions(RAW_DIR / "TRIZ_contradictions.csv")
    principles_list = load_matrix(RAW_DIR / "TRIZ_matrix.csv")

    print(f"  Parameters: {len(params)}")
    print(f"  Contradiction pairs: {len(pairs)}")
    print(f"  Matrix rows: {len(principles_list)}")

    assert len(pairs) == len(principles_list), (
        f"Mismatch: {len(pairs)} pairs vs {len(principles_list)} matrix rows"
    )

    # Use all templates per pair to ensure full coverage in train/test split.
    # With 20 templates × 1482 pairs, this gives ~29k samples — the model needs
    # every template+pair combination in training to generalize.
    num_templates = len(ALL_TEMPLATES)
    print(f"Generating training samples ({num_templates} templates per pair)...")
    samples = generate_samples(
        params, pairs, principles_list, templates_per_pair=num_templates
    )

    # Write JSONL
    jsonl_path = OUT_DIR / "triz_labels.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"  Wrote {len(samples)} samples to {jsonl_path}")

    # Write stats
    stats = compute_stats(samples)
    stats_path = OUT_DIR / "triz_labels_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"  Stats: {stats_path}")

    # Summary
    print(f"\nDataset summary:")
    print(f"  Samples:          {stats['num_samples']}")
    print(f"  Unique labels:    {stats['unique_labels']}/40")
    print(f"  Missing labels:   {stats['missing_labels'] or 'None'}")
    print(f"  Avg labels/sample: {stats['avg_labels_per_sample']}")
    print(f"  Min label freq:   {stats['min_label_frequency']}")
    print(f"  Max label freq:   {stats['max_label_frequency']}")

    if stats["missing_labels"]:
        print(f"\n  WARNING: Labels {stats['missing_labels']} are missing!")
    if stats["num_samples"] < 500:
        print(f"\n  WARNING: Only {stats['num_samples']} samples (target: 500+)")


if __name__ == "__main__":
    main()
