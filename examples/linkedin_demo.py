"""Screen-recording demo for DocFrame.

Run from the repository root:
    python3 examples/linkedin_demo.py
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import docframe as df


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "test_corpus"


def pick_demo_files() -> list[Path]:
    """Pick a small, visual set of files for a short demo."""

    candidates: list[Path] = []

    for folder, pattern in (
        (CORPUS / "pdf", "*.pdf"),
        (CORPUS / "doc", "*.doc"),
        (CORPUS / "csv", "*.csv"),
    ):
        if folder.exists():
            first = next(iter(sorted(folder.glob(pattern))), None)
            if first is not None:
                candidates.append(first)

    fallback = ROOT / "examples" / "sample.csv"
    if not candidates and fallback.exists():
        candidates.append(fallback)

    return candidates


def print_banner() -> None:
    """Print a concise intro for the recording."""

    print()
    print("============================================================")
    print("DocFrame: Python document processing for AI-ready workflows")
    print("============================================================")
    print("Install: pip install docframe-ai")
    print("Import:  import docframe as df")
    print()


def preview_text(text: str, *, limit: int = 280) -> str:
    """Return a compact one-line text preview."""

    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit].rstrip()}..."


def print_result(result: df.DocumentResult) -> None:
    """Print one processed document in a recording-friendly format."""

    print(f"File:    {result.metadata.filename}")
    print(f"Type:    {result.metadata.document_type}")
    print(f"Size:    {result.metadata.size_bytes:,} bytes")
    print(f"Chunks:  {len(result.chunks)}")

    if result.errors:
        print(f"Errors:  {result.errors}")
    if result.warnings:
        print(f"Warning: {result.warnings[0]}")

    if result.text:
        print(f"Preview: {preview_text(result.text)}")
    elif result.table_count:
        table = next(chunk for chunk in result.chunks if chunk.rows)
        print(f"Rows:    {len(table.rows or [])} extracted from first table chunk")
        if table.rows:
            print(f"Sample:  {table.rows[0]}")
    else:
        print("Preview: Metadata extracted; no text/table content emitted.")

    print("-" * 60)


def print_llm_payload(results: list[df.DocumentResult]) -> None:
    """Print the simplified LLM-ready output for the recording."""

    payload = df.to_llm_payload(results, max_chars=650)
    tokens = payload["tokens"]

    print()
    print("LLM-ready output:")
    print("-" * 60)
    print(f"Schema: {payload['schema']}")
    print(f"Token blocks: {payload['token_count']}")
    print()
    print("First token block:")
    print(tokens[0] if tokens else "No text/table token blocks emitted.")
    print()
    print("Payload shape:")
    print(json.dumps({"schema": payload["schema"], "tokens": ["..."]}, indent=2))
    print("-" * 60)


async def main() -> None:
    """Run the demo."""

    paths = pick_demo_files()
    if not paths:
        raise SystemExit("No demo files found. Add files to test_corpus or examples/sample.csv.")

    print_banner()
    print("Processing files:")
    for path in paths:
        print(f"  - {path.relative_to(ROOT)}")
    print()

    framework = df.DocFrame(
        options=df.ProcessingOptions(
            max_concurrency=4,
            max_table_rows=5,
            max_chars_per_text_chunk=3_000,
        )
    )
    results = await framework.process_many(paths, continue_on_error=True)

    print("Normalized output:")
    print("-" * 60)
    for result in results:
        print_result(result)

    print_llm_payload(results)

    print()
    print("One API. One CLI. Messy documents into LLM-ready token blocks.")
    print("CLI: docframe process ./documents --recursive --format llm")
    print("GitHub: https://github.com/Meet2147/docframe")
    print()


if __name__ == "__main__":
    asyncio.run(main())
