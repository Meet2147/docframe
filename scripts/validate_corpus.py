"""Validate a real document corpus against DocFrame.

The validator is intentionally separate from the package runtime. It is a
release-readiness tool for local corpora that may be large, private, or messy.

Examples:
    python3 scripts/validate_corpus.py test_corpus
    python3 scripts/validate_corpus.py test_corpus --out corpus-report.json
    python3 scripts/validate_corpus.py test_corpus --limit 100 --max-concurrency 4
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import docframe as df


def collect_corpus_paths(root: Path, framework: df.DocFrame, *, limit: int | None = None) -> tuple[list[Path], Counter[str]]:
    """Collect supported corpus paths and count unsupported suffixes."""

    supported = set(framework.registry.supported_extensions())
    paths: list[Path] = []
    unsupported: Counter[str] = Counter()

    for candidate in sorted(root.rglob("*")):
        if not candidate.is_file():
            continue
        suffix = candidate.suffix.lower() or "<none>"
        if suffix in supported:
            paths.append(candidate)
            if limit is not None and len(paths) >= limit:
                break
        else:
            unsupported[suffix] += 1

    return paths, unsupported


def summarize_result(result: df.DocumentResult, duration_seconds: float) -> dict[str, Any]:
    """Return a compact per-document summary."""

    table_rows = sum(len(chunk.rows or []) for chunk in result.chunks if chunk.rows is not None)
    text_chars = sum(len(chunk.text or "") for chunk in result.chunks)
    return {
        "path": result.metadata.source_path,
        "filename": result.metadata.filename,
        "type": result.metadata.document_type,
        "size_bytes": result.metadata.size_bytes,
        "chunks": len(result.chunks),
        "text_chars": text_chars,
        "table_rows": table_rows,
        "warnings": result.warnings,
        "errors": result.errors,
        "duration_seconds": round(duration_seconds, 4),
    }


async def process_one(path: Path, framework: df.DocFrame) -> dict[str, Any]:
    """Process one path and return a compact summary."""

    started = time.perf_counter()
    result = await framework.process_safe(path)
    return summarize_result(result, time.perf_counter() - started)


async def validate_corpus(args: argparse.Namespace) -> dict[str, Any]:
    """Run a bounded-concurrency corpus validation pass."""

    root = args.root.expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Corpus directory does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Corpus path is not a directory: {root}")

    framework = df.DocFrame(
        options=df.ProcessingOptions(
            max_chars_per_text_chunk=args.max_chars,
            max_table_rows=args.max_rows,
            max_concurrency=args.max_concurrency,
        )
    )
    paths, unsupported = collect_corpus_paths(root, framework, limit=args.limit)
    semaphore = asyncio.Semaphore(args.max_concurrency)

    async def bounded(path: Path) -> dict[str, Any]:
        async with semaphore:
            return await process_one(path, framework)

    started = time.perf_counter()
    tasks = [asyncio.create_task(bounded(path)) for path in paths]
    results: list[dict[str, Any]] = []

    for index, task in enumerate(asyncio.as_completed(tasks), start=1):
        result = await task
        results.append(result)
        if not args.quiet and (index == len(tasks) or index % args.progress_every == 0):
            print(f"Processed {index}/{len(tasks)}")

    elapsed = time.perf_counter() - started
    by_type: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "files": 0,
            "errors": 0,
            "warnings": 0,
            "chunks": 0,
            "text_chars": 0,
            "table_rows": 0,
        }
    )
    error_samples: list[dict[str, Any]] = []
    warning_samples: list[dict[str, Any]] = []
    warning_counts: Counter[str] = Counter()
    error_counts: Counter[str] = Counter()

    for result in results:
        type_summary = by_type[result["type"]]
        type_summary["files"] += 1
        type_summary["errors"] += int(bool(result["errors"]))
        type_summary["warnings"] += int(bool(result["warnings"]))
        type_summary["chunks"] += result["chunks"]
        type_summary["text_chars"] += result["text_chars"]
        type_summary["table_rows"] += result["table_rows"]

        if result["errors"]:
            error_counts.update(result["errors"])
        if result["errors"] and len(error_samples) < args.sample_limit:
            error_samples.append(
                {
                    "path": result["path"],
                    "type": result["type"],
                    "errors": result["errors"],
                }
            )
        if result["warnings"]:
            warning_counts.update(result["warnings"])
        if result["warnings"] and len(warning_samples) < args.sample_limit:
            warning_samples.append(
                {
                    "path": result["path"],
                    "type": result["type"],
                    "warnings": result["warnings"],
                }
            )

    report = {
        "root": str(root),
        "elapsed_seconds": round(elapsed, 4),
        "processed_files": len(results),
        "unsupported_files": sum(unsupported.values()),
        "unsupported_by_extension": dict(sorted(unsupported.items())),
        "by_type": dict(sorted(by_type.items())),
        "error_files": sum(1 for result in results if result["errors"]),
        "warning_files": sum(1 for result in results if result["warnings"]),
        "errors_by_message": dict(error_counts.most_common()),
        "warnings_by_message": dict(warning_counts.most_common()),
        "error_samples": error_samples,
        "warning_samples": warning_samples,
    }
    return report


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Validate a corpus against DocFrame.")
    parser.add_argument("root", type=Path, help="Corpus root directory.")
    parser.add_argument("--out", type=Path, help="Optional JSON report path.")
    parser.add_argument("--limit", type=int, help="Process only the first N supported files.")
    parser.add_argument("--max-concurrency", type=int, default=8)
    parser.add_argument("--max-rows", type=int, default=1_000)
    parser.add_argument("--max-chars", type=int, default=20_000)
    parser.add_argument("--progress-every", type=int, default=100)
    parser.add_argument("--sample-limit", type=int, default=20)
    parser.add_argument(
        "--allow-errors",
        action="store_true",
        help="Return exit code 0 even when some files produce structured errors.",
    )
    parser.add_argument("--quiet", action="store_true", help="Only print the final report.")
    return parser.parse_args()


def main() -> None:
    """Run the corpus validator."""

    args = parse_args()
    report = asyncio.run(validate_corpus(args))
    rendered = json.dumps(report, indent=2)

    if args.out:
        args.out.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {args.out}")
    print(rendered)

    if report["error_files"] and not args.allow_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
