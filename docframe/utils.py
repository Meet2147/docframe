"""Small filesystem and serialization helpers."""

from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path

from .models import DocumentMetadata, DocumentType

EXTENSION_TYPES: dict[str, DocumentType] = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".csv": "csv",
    ".xlsx": "xlsx",
    ".xlsm": "xlsx",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
}


def sha256_file(path: Path) -> str:
    """Return a streaming SHA-256 digest for a file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def detect_document_type(path: Path) -> DocumentType:
    """Infer a document type from the file extension."""

    return EXTENSION_TYPES.get(path.suffix.lower(), "unknown")


def build_metadata(path: Path) -> DocumentMetadata:
    """Build base metadata common to every adapter."""

    resolved = path.expanduser().resolve()
    mime_type, _ = mimetypes.guess_type(str(resolved))
    return DocumentMetadata(
        source_path=str(resolved),
        filename=resolved.name,
        extension=resolved.suffix.lower(),
        document_type=detect_document_type(resolved),
        mime_type=mime_type or "application/octet-stream",
        size_bytes=resolved.stat().st_size,
        sha256=sha256_file(resolved),
    )


def split_text(text: str, *, max_chars: int) -> list[str]:
    """Split large text into bounded chunks without losing content."""

    if len(text) <= max_chars:
        return [text]
    return [text[index : index + max_chars] for index in range(0, len(text), max_chars)]

