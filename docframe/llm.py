"""LLM-ready token block helpers.

DocFrame keeps rich document models as the source of truth, then projects them
into small source-grounded token blocks for model prompts and RAG pipelines.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable

from .models import DocumentChunk, DocumentResult


DEFAULT_TOKEN_CHARS = 2_000


def to_llm_tokens(
    results: DocumentResult | Iterable[DocumentResult],
    *,
    max_chars: int = DEFAULT_TOKEN_CHARS,
    include_source: bool = True,
) -> list[str]:
    """Convert one or more processed documents into LLM-ready text tokens.

    These are token blocks, not model-specific token IDs. Real LLM tokenization
    varies by provider and model, so DocFrame emits bounded plain-text blocks
    that can be passed directly into prompts, chat messages, embedding jobs, or
    retrieval indexes.
    """

    result_list = [results] if isinstance(results, DocumentResult) else list(results)
    tokens: list[str] = []
    for result in result_list:
        tokens.extend(
            token
            for chunk in result.chunks
            for token in chunk_to_llm_tokens(
                result,
                chunk,
                max_chars=max_chars,
                include_source=include_source,
            )
        )
    return tokens


def to_llm_prompt(
    results: DocumentResult | Iterable[DocumentResult],
    *,
    max_chars: int = DEFAULT_TOKEN_CHARS,
    include_source: bool = True,
) -> str:
    """Convert processed documents into one prompt-ready string."""

    return "\n\n".join(
        to_llm_tokens(results, max_chars=max_chars, include_source=include_source)
    )


def to_llm_payload(
    results: DocumentResult | Iterable[DocumentResult],
    *,
    max_chars: int = DEFAULT_TOKEN_CHARS,
    include_source: bool = True,
) -> dict[str, object]:
    """Return a compact SAGER-style LLM payload.

    SAGER here means source-grounded atomic evidence records: each token block is
    small enough for model context windows and carries its source directly in
    the text when requested.
    """

    tokens = to_llm_tokens(results, max_chars=max_chars, include_source=include_source)
    return {
        "schema": "docframe.sager.tokens.v1",
        "token_count": len(tokens),
        "tokens": tokens,
    }


def chunk_to_llm_tokens(
    result: DocumentResult,
    chunk: DocumentChunk,
    *,
    max_chars: int,
    include_source: bool,
) -> list[str]:
    """Convert one normalized chunk into one or more LLM token blocks."""

    text = chunk_to_text(chunk)
    if not text:
        return []

    prefix = source_prefix(result, chunk) if include_source else ""
    available_chars = max(1, max_chars - len(prefix) - 1)
    parts = split_token_text(text, max_chars=available_chars)
    if not prefix:
        return parts
    return [f"{prefix}\n{part}" for part in parts]


def chunk_to_text(chunk: DocumentChunk) -> str:
    """Project a normalized chunk into plain text."""

    if chunk.type == "text" and chunk.text:
        return clean_text(chunk.text)
    if chunk.type == "table" and chunk.rows:
        return table_rows_to_text(chunk.rows)
    return ""


def table_rows_to_text(rows: list[dict[str, object]]) -> str:
    """Turn table rows into compact key-value text lines."""

    lines: list[str] = []
    for row_index, row in enumerate(rows, start=1):
        fields = [
            f"{key}: {value}"
            for key, value in row.items()
            if value is not None and str(value).strip()
        ]
        if fields:
            lines.append(f"row {row_index}: " + " | ".join(fields))
    return "\n".join(lines)


def source_prefix(result: DocumentResult, chunk: DocumentChunk) -> str:
    """Build a source-grounding prefix for a token block."""

    parts = [
        f"source={result.metadata.filename}",
        f"type={result.metadata.document_type}",
        f"chunk={chunk.id}",
    ]
    if chunk.page is not None:
        parts.append(f"page={chunk.page}")
    if chunk.sheet is not None:
        parts.append(f"sheet={chunk.sheet}")
    return "[" + " ".join(parts) + "]"


def clean_text(text: str) -> str:
    """Normalize whitespace without removing meaningful line breaks."""

    normalized_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in normalized_lines if line)


def split_token_text(text: str, *, max_chars: int) -> list[str]:
    """Split text into bounded blocks at natural boundaries where possible."""

    text = clean_text(text)
    if len(text) <= max_chars:
        return [text] if text else []

    tokens: list[str] = []
    current: list[str] = []
    current_size = 0

    for paragraph in re.split(r"\n{2,}|\n", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) > max_chars:
            if current:
                tokens.append("\n".join(current))
                current = []
                current_size = 0
            tokens.extend(split_long_text(paragraph, max_chars=max_chars))
            continue

        separator_size = 1 if current else 0
        if current and current_size + separator_size + len(paragraph) > max_chars:
            tokens.append("\n".join(current))
            current = [paragraph]
            current_size = len(paragraph)
        else:
            current.append(paragraph)
            current_size += separator_size + len(paragraph)

    if current:
        tokens.append("\n".join(current))
    return tokens


def split_long_text(text: str, *, max_chars: int) -> list[str]:
    """Split a long paragraph while preserving words when possible."""

    words = text.split()
    if not words:
        return []

    tokens: list[str] = []
    current: list[str] = []
    current_size = 0
    for word in words:
        if len(word) > max_chars:
            if current:
                tokens.append(" ".join(current))
                current = []
                current_size = 0
            tokens.extend(word[index : index + max_chars] for index in range(0, len(word), max_chars))
            continue

        separator_size = 1 if current else 0
        if current and current_size + separator_size + len(word) > max_chars:
            tokens.append(" ".join(current))
            current = [word]
            current_size = len(word)
        else:
            current.append(word)
            current_size += separator_size + len(word)

    if current:
        tokens.append(" ".join(current))
    return tokens


def dumps_llm_payload(payload: dict[str, object]) -> str:
    """Serialize an LLM payload as stable JSON."""

    return json.dumps(payload, indent=2, ensure_ascii=False)
