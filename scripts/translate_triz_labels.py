"""Translate only the `text` field in a JSONL dataset.

Default backend uses Google Translate's unofficial public endpoint
(`translate.googleapis.com`) so no paid key is required.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

TRANSLATION_ERRORS = (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError)


def translate_via_google_public(text: str, target_lang: str = "ko", timeout: float = 20.0) -> str:
    """Translate text using Google's public translate endpoint (no API key)."""
    if not text.strip():
        return text

    params = urllib.parse.urlencode(
        {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text,
        }
    )
    url = f"https://translate.googleapis.com/translate_a/single?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Patent-GPT-Translator/1.0"})

    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = response.read().decode("utf-8")

    data = json.loads(payload)
    # Format is typically: [[["translated", "original", ...], ...], ...]
    translated = "".join(part[0] for part in data[0] if part and part[0])
    return translated or text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate `text` field in JSONL and keep all other fields unchanged."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/training/triz_labels.jsonl"),
        help="Input JSONL path",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/training/triz_labels.ko.jsonl"),
        help="Output JSONL path",
    )
    parser.add_argument(
        "--target-lang",
        type=str,
        default="ko",
        help="Target language code (default: ko)",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.1,
        help="Delay between requests to reduce rate-limit risk",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Retries per row on translation failure",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Translate only first N lines (0 = all)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it already exists",
    )
    return parser.parse_args()


def translate_with_retry(text: str, target_lang: str, max_retries: int) -> str:
    for attempt in range(1, max_retries + 1):
        try:
            return translate_via_google_public(text=text, target_lang=target_lang)
        except TRANSLATION_ERRORS:
            if attempt == max_retries:
                raise
            # Small exponential backoff
            time.sleep(0.5 * attempt)
    return text


def main() -> None:
    args = parse_args()
    input_path = args.input
    output_path = args.output

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if output_path.exists() and not args.overwrite:
        raise FileExistsError(
            f"Output already exists: {output_path}. "
            "Use --overwrite or set a different --output path."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    success = 0
    failed = 0

    with input_path.open("r", encoding="utf-8") as rf, output_path.open(
        "w", encoding="utf-8"
    ) as wf:
        for line in rf:
            if args.limit and total >= args.limit:
                break

            total += 1
            raw = line.strip()
            if not raw:
                continue

            try:
                row: dict[str, Any] = json.loads(raw)
            except json.JSONDecodeError as exc:
                failed += 1
                print(f"[WARN] line {total}: invalid JSON ({exc})")
                continue

            text = row.get("text")
            if isinstance(text, str):
                try:
                    row["text"] = translate_with_retry(
                        text=text, target_lang=args.target_lang, max_retries=args.max_retries
                    )
                    success += 1
                except TRANSLATION_ERRORS as exc:
                    failed += 1
                    print(f"[WARN] line {total}: translation failed ({exc})")
                    # Keep original text on failure.
            else:
                failed += 1
                print(f"[WARN] line {total}: missing or non-string `text` field")

            wf.write(json.dumps(row, ensure_ascii=False) + "\n")

            if args.sleep_seconds > 0:
                time.sleep(args.sleep_seconds)

            if total % 200 == 0:
                print(
                    f"[INFO] processed={total} success={success} failed={failed} "
                    f"output={output_path}"
                )

    print(f"[DONE] processed={total} success={success} failed={failed} output={output_path}")


if __name__ == "__main__":
    main()
