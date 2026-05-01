"""Screen-recording demo for DocFrame.

Run from the repository root:
    python3 examples/linkedin_demo.py
"""

from __future__ import annotations

import asyncio
import os
import json
import shutil
import sys
import textwrap
from pathlib import Path

import docframe as df


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "test_corpus"
WIDTH = min(shutil.get_terminal_size((92, 24)).columns, 96)


class Style:
    """ANSI styling helpers for a nicer terminal recording."""

    enabled = os.environ.get("NO_COLOR") is None and sys.stdout.isatty()
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BLUE = "\033[38;5;39m"
    GREEN = "\033[38;5;42m"
    CYAN = "\033[38;5;51m"
    YELLOW = "\033[38;5;220m"
    MAGENTA = "\033[38;5;171m"
    GRAY = "\033[38;5;245m"


def paint(text: str, color: str, *, bold: bool = False) -> str:
    """Colorize text when ANSI output is enabled."""

    if not Style.enabled:
        return text
    prefix = f"{Style.BOLD if bold else ''}{color}"
    return f"{prefix}{text}{Style.RESET}"


def hr(char: str = "-") -> str:
    """Return a horizontal rule sized for the terminal."""

    return char * WIDTH


def section(title: str, subtitle: str | None = None) -> None:
    """Print a styled section heading."""

    print()
    print(paint(hr("="), Style.BLUE))
    print(paint(title, Style.CYAN, bold=True))
    if subtitle:
        print(paint(subtitle, Style.GRAY))
    print(paint(hr("="), Style.BLUE))


def label(name: str, value: object, *, color: str = Style.GREEN) -> None:
    """Print a small label/value line."""

    name_text = f"{name}:".ljust(18)
    print(f"{paint(name_text, color, bold=True)} {value}")


def wrap_block(text: str, *, indent: str = "  ", width: int = WIDTH - 4) -> str:
    """Wrap a block of text while preserving separate lines."""

    lines: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            lines.append("")
            continue
        lines.extend(textwrap.wrap(line, width=width) or [""])
    return textwrap.indent("\n".join(lines), indent)


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

    section(
        "DocFrame",
        "Python document processing for LLM-ready workflows",
    )
    label("Install", "pip install docframe-ai", color=Style.YELLOW)
    label("Python import", "import docframe as df", color=Style.YELLOW)
    label("CLI", "docframe process ./documents --recursive --format llm", color=Style.YELLOW)


def preview_text(text: str, *, limit: int = 720) -> str:
    """Return a generous text preview."""

    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit].rstrip()}..."


def preview_block(text: str, *, limit: int = 720) -> str:
    """Return a wrapped preview block for screen recording."""

    return wrap_block(preview_text(text, limit=limit))


def sample_row(row: dict[str, object], *, limit: int = 4) -> str:
    """Return a compact sample of a table row."""

    visible = dict(list(row.items())[:limit])
    suffix = " ..." if len(row) > limit else ""
    return f"{json.dumps(visible, ensure_ascii=False)}{suffix}"


def print_result(result: df.DocumentResult) -> None:
    """Print one processed document in a recording-friendly format."""

    print(paint(result.metadata.filename, Style.MAGENTA, bold=True))
    label("Type", result.metadata.document_type)
    label("Size", f"{result.metadata.size_bytes:,} bytes")
    label("Chunks", len(result.chunks))

    if result.errors:
        label("Errors", result.errors, color=Style.YELLOW)
    if result.warnings:
        label("Warning", preview_text(result.warnings[0], limit=100), color=Style.YELLOW)

    if result.text:
        label("Preview", "")
        print(preview_block(result.text))
    elif result.table_count:
        table = next(chunk for chunk in result.chunks if chunk.rows)
        label("Rows", f"{len(table.rows or [])} extracted from first table chunk")
        if table.rows:
            label("Sample", sample_row(table.rows[0]))
    else:
        label("Preview", "Metadata extracted; no text/table content emitted.")

    print(paint(hr(), Style.GRAY))


def print_llm_payload(results: list[df.DocumentResult]) -> None:
    """Print the simplified LLM-ready output for the recording."""

    payload = df.to_llm_payload(results, max_chars=650)
    tokens = payload["tokens"]

    section(
        "LLM-ready output",
        "SAGER-style source-grounded atomic evidence records",
    )
    label("Schema", payload["schema"], color=Style.CYAN)
    label("Token blocks", payload["token_count"], color=Style.CYAN)
    print()
    print(paint("First token block", Style.MAGENTA, bold=True))
    print(wrap_block(tokens[0] if tokens else "No text/table token blocks emitted."))
    print()
    print(paint("Payload shape", Style.MAGENTA, bold=True))
    print(wrap_block(json.dumps({"schema": payload["schema"], "tokens": ["..."]}, indent=2)))
    print(paint(hr(), Style.GRAY))


def print_file_list(paths: list[Path]) -> None:
    """Print selected files in a compact table."""

    section("Input files", "PDF + Word + CSV flowing through one API")
    for index, path in enumerate(paths, start=1):
        print(f"{paint(str(index) + '.', Style.BLUE, bold=True)} {path.relative_to(ROOT)}")


async def main() -> None:
    """Run the demo."""

    paths = pick_demo_files()
    if not paths:
        raise SystemExit("No demo files found. Add files to test_corpus or examples/sample.csv.")

    print_banner()
    print_file_list(paths)

    framework = df.DocFrame(
        options=df.ProcessingOptions(
            max_concurrency=4,
            max_table_rows=5,
            max_chars_per_text_chunk=3_000,
        )
    )
    results = await framework.process_many(paths, continue_on_error=True)

    section("Normalized document output", "Rich structured records from messy files")
    for result in results:
        print_result(result)

    print_llm_payload(results)

    section("Ready for developers")
    label("One API", "messy documents into LLM-ready token blocks", color=Style.CYAN)
    label("CLI", "docframe process ./documents --recursive --format llm", color=Style.CYAN)
    label("GitHub", "https://github.com/Meet2147/docframe", color=Style.CYAN)
    print()


if __name__ == "__main__":
    asyncio.run(main())
