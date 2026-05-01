"""Command line interface for DocFrame."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from .core import DocFrame
from .models import ProcessingOptions
from .writers import OutputFormat, render_results


def main(argv: list[str] | None = None) -> None:
    """Run the DocFrame CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "process":
        asyncio.run(process_command(args))
        return
    if args.command == "formats":
        framework = DocFrame()
        print("\n".join(framework.registry.supported_extensions()))
        return

    parser.print_help()


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""

    parser = argparse.ArgumentParser(
        prog="docframe",
        description="Process PDFs, DOCX, CSV, Excel, JPG, and PNG through DocFrame.",
    )
    commands = parser.add_subparsers(dest="command")

    process = commands.add_parser("process", help="Process one file or a directory.")
    process.add_argument("input", help="Input file or directory.")
    process.add_argument("--out", help="Write output to a file instead of stdout.")
    process.add_argument(
        "--format",
        choices=("json", "text", "markdown"),
        default="json",
        help="Output format.",
    )
    process.add_argument("--max-rows", type=int, default=1_000)
    process.add_argument("--max-chars", type=int, default=20_000)
    process.add_argument("--max-concurrency", type=int, default=8)
    process.add_argument(
        "--recursive",
        action="store_true",
        help="Recurse through directories.",
    )

    commands.add_parser("formats", help="List supported file extensions.")
    return parser


async def process_command(args: argparse.Namespace) -> None:
    """Process input and print or write output."""

    options = ProcessingOptions(
        max_table_rows=args.max_rows,
        max_chars_per_text_chunk=args.max_chars,
        max_concurrency=args.max_concurrency,
    )
    framework = DocFrame(options=options)
    paths = collect_paths(Path(args.input), recursive=args.recursive, framework=framework)
    results = await framework.process_many(paths, continue_on_error=True)
    rendered = render_results(results, output_format=args.format)

    if args.out:
        Path(args.out).write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.out}")
        return
    print(rendered)


def collect_paths(path: Path, *, recursive: bool, framework: DocFrame) -> list[Path]:
    """Collect processable paths from a file or directory."""

    resolved = path.expanduser().resolve()
    if resolved.is_file():
        return [resolved]
    if not resolved.is_dir():
        raise SystemExit(f"Input does not exist: {resolved}")

    pattern = "**/*" if recursive else "*"
    supported = set(framework.registry.supported_extensions())
    paths = [
        candidate
        for candidate in resolved.glob(pattern)
        if candidate.is_file() and candidate.suffix.lower() in supported
    ]
    if not paths:
        raise SystemExit(f"No supported documents found in {resolved}")
    return sorted(paths)


if __name__ == "__main__":
    main()
