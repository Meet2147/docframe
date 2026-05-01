"""Output renderers for processed documents."""

from __future__ import annotations

import json
from typing import Literal

from .llm import DEFAULT_TOKEN_CHARS, dumps_llm_payload, to_llm_payload, to_llm_prompt, to_llm_tokens
from .models import DocumentResult

OutputFormat = Literal["json", "text", "markdown", "tokens", "llm", "prompt"]


def render_result(
    result: DocumentResult,
    *,
    output_format: OutputFormat,
    token_chars: int = DEFAULT_TOKEN_CHARS,
) -> str:
    """Render a single result."""

    if output_format == "json":
        return result.model_dump_json(indent=2)
    if output_format == "text":
        return result.text
    if output_format == "markdown":
        return render_markdown(result)
    if output_format == "tokens":
        return json.dumps(to_llm_tokens(result, max_chars=token_chars), indent=2, ensure_ascii=False)
    if output_format == "llm":
        return dumps_llm_payload(to_llm_payload(result, max_chars=token_chars))
    if output_format == "prompt":
        return to_llm_prompt(result, max_chars=token_chars)
    raise ValueError(f"Unsupported output format: {output_format}")


def render_results(
    results: list[DocumentResult],
    *,
    output_format: OutputFormat,
    token_chars: int = DEFAULT_TOKEN_CHARS,
) -> str:
    """Render one or more results."""

    if output_format == "tokens":
        return json.dumps(
            to_llm_tokens(results, max_chars=token_chars),
            indent=2,
            ensure_ascii=False,
        )
    if output_format == "llm":
        return dumps_llm_payload(to_llm_payload(results, max_chars=token_chars))
    if output_format == "prompt":
        return to_llm_prompt(results, max_chars=token_chars)
    if len(results) == 1:
        return render_result(results[0], output_format=output_format, token_chars=token_chars)
    if output_format == "json":
        return json.dumps([result.model_dump(mode="json") for result in results], indent=2)
    return "\n\n---\n\n".join(
        render_result(result, output_format=output_format, token_chars=token_chars)
        for result in results
    )


def render_markdown(result: DocumentResult) -> str:
    """Render a human-readable Markdown preview."""

    lines = [
        f"# {result.metadata.filename}",
        "",
        f"- Type: `{result.metadata.document_type}`",
        f"- Size: `{result.metadata.size_bytes}` bytes",
        f"- Chunks: `{len(result.chunks)}`",
    ]
    if result.warnings:
        lines.append(f"- Warnings: `{len(result.warnings)}`")
    lines.append("")

    for chunk in result.chunks:
        if chunk.type == "text" and chunk.text:
            label = f"page {chunk.page}" if chunk.page is not None else "text"
            lines.extend([f"## {label}", "", chunk.text, ""])
        if chunk.type == "table" and chunk.rows is not None:
            lines.extend([f"## table {chunk.sheet or ''}".strip(), ""])
            lines.append(f"Rows extracted: `{len(chunk.rows)}`")
            lines.append("")
        if chunk.type == "image":
            lines.extend(["## image", "", json.dumps(chunk.metadata, indent=2), ""])

    return "\n".join(lines).strip() + "\n"
