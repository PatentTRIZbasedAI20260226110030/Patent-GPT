"""Translate only the `text` field in a JSONL dataset.

Default backend uses Google Translate's unofficial public endpoint
(`translate.googleapis.com`) so no paid key is required.
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

TRANSLATION_ERRORS = (
    urllib.error.URLError,
    TimeoutError,
    ConnectionError,
    ConnectionResetError,
    ConnectionAbortedError,
    BrokenPipeError,
    socket.timeout,
    http.client.RemoteDisconnected,
    OSError,
    json.JSONDecodeError,
    ValueError,
)


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
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing .tmp file created by a previous interrupted run",
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
    if output_path.exists() and not args.overwrite and not args.resume:
        raise FileExistsError(
            f"Output already exists: {output_path}. "
            "Use --overwrite or set a different --output path."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_output_path = output_path.with_suffix(f"{output_path.suffix}.tmp")

    resume_from_line = 0
    write_mode = "w"

    if args.resume:
        if not tmp_output_path.exists():
            raise FileNotFoundError(
                f"Resume requested but tmp file does not exist: {tmp_output_path}"
            )
        with tmp_output_path.open("r", encoding="utf-8") as tmpf:
            resume_from_line = sum(1 for _ in tmpf)
        write_mode = "a"
        print(f"[INFO] resume enabled: starting from line {resume_from_line + 1}")
    elif tmp_output_path.exists():
        if args.overwrite:
            tmp_output_path.unlink()
        else:
            raise FileExistsError(
                f"Temporary output already exists: {tmp_output_path}. "
                "Use --overwrite to replace it or --resume to continue."
            )

    total = 0
    success = 0
    failed = 0

    with input_path.open("r", encoding="utf-8") as rf, tmp_output_path.open(
        write_mode, encoding="utf-8"
    ) as wf:
        skipped = 0
        for line in rf:
            if skipped < resume_from_line:
                skipped += 1
                continue

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
                processed_global = resume_from_line + total
                print(
                    f"[INFO] processed={processed_global} success={success} failed={failed} "
                    f"output={output_path}"
                )

    # Atomic replace prevents partial/corrupted final output on interruption.
    os.replace(tmp_output_path, output_path)
    processed_global = resume_from_line + total
    print(
        f"[DONE] processed={processed_global} success={success} failed={failed} "
        f"output={output_path}"
    )


if __name__ == "__main__":
    main()
