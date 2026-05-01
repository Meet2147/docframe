"""Collect PDFs from a nested directory tree into one flat directory.

Examples:
    python3 scripts/collect_pdfs.py "/path/to/archive" "/path/to/all_pdfs" --dry-run
    python3 scripts/collect_pdfs.py "/path/to/archive" "/path/to/all_pdfs"
    python3 scripts/collect_pdfs.py "/path/to/archive" "/path/to/all_pdfs" --move
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CollectionSummary:
    """Result counts for a PDF collection run."""

    discovered: int = 0
    copied: int = 0
    moved: int = 0
    skipped: int = 0


def _is_relative_to(child: Path, parent: Path) -> bool:
    """Return True when child is inside parent."""

    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def _stable_collision_name(path: Path, source_root: Path) -> str:
    """Build a stable filename when two PDFs share the same basename."""

    relative = path.relative_to(source_root).as_posix()
    digest = hashlib.sha1(relative.encode("utf-8")).hexdigest()[:10]
    return f"{path.stem}__{digest}{path.suffix.lower()}"


def _target_for(path: Path, source_root: Path, destination: Path, reserved: set[Path]) -> Path:
    """Return a non-conflicting target path for a source PDF."""

    candidate = destination / path.name
    if candidate not in reserved and not candidate.exists():
        reserved.add(candidate)
        return candidate

    candidate = destination / _stable_collision_name(path, source_root)
    if candidate not in reserved and not candidate.exists():
        reserved.add(candidate)
        return candidate

    index = 2
    while True:
        numbered = candidate.with_name(f"{candidate.stem}_{index}{candidate.suffix}")
        if numbered not in reserved and not numbered.exists():
            reserved.add(numbered)
            return numbered
        index += 1


def iter_pdfs(source: Path, destination: Path) -> list[Path]:
    """Find PDFs recursively, excluding PDFs already inside the destination."""

    source = source.resolve()
    destination = destination.resolve()

    return sorted(
        path
        for path in source.rglob("*")
        if path.is_file()
        and path.suffix.lower() == ".pdf"
        and not _is_relative_to(path.resolve(), destination)
    )


def collect_pdfs(
    source: Path,
    destination: Path,
    *,
    move: bool = False,
    dry_run: bool = False,
    quiet: bool = False,
) -> CollectionSummary:
    """Copy or move every PDF under source into destination.

    Duplicate basenames are handled with a stable SHA-1 suffix derived from the
    source-relative path. Existing destination files are never overwritten.
    """

    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {source}")

    pdfs = iter_pdfs(source, destination)
    reserved: set[Path] = set()

    if not dry_run:
        destination.mkdir(parents=True, exist_ok=True)

    copied = 0
    moved = 0
    skipped = 0

    for pdf in pdfs:
        target = _target_for(pdf, source, destination, reserved)
        if not quiet:
            print(f"{'MOVE' if move else 'COPY'} {pdf} -> {target}")

        if dry_run:
            continue

        if move:
            shutil.move(str(pdf), str(target))
            moved += 1
        else:
            shutil.copy2(pdf, target)
            copied += 1

    return CollectionSummary(
        discovered=len(pdfs),
        copied=copied,
        moved=moved,
        skipped=skipped,
    )


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Collect PDFs from nested folders into one flat directory."
    )
    parser.add_argument("source", type=Path, help="Directory to scan recursively.")
    parser.add_argument("destination", type=Path, help="Directory where PDFs will be collected.")
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move PDFs instead of copying them. Copying is the default.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without creating or copying files.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print the final summary.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the PDF collector CLI."""

    args = parse_args()
    summary = collect_pdfs(
        args.source,
        args.destination,
        move=args.move,
        dry_run=args.dry_run,
        quiet=args.quiet,
    )

    action = "moved" if args.move else "copied"
    if args.dry_run:
        action = "would be copied" if not args.move else "would be moved"

    print()
    completed = summary.discovered if args.dry_run else summary.moved if args.move else summary.copied

    print(f"Discovered: {summary.discovered}")
    print(f"PDFs {action}: {completed}")


if __name__ == "__main__":
    main()
