"""Output renderers for processed documents."""

from __future__ import annotations

import json
from typing import Literal

from .models import DocumentResult

OutputFormat = Literal["json", "text", "markdown"]


def render_result(result: DocumentResult, *, output_format: OutputFormat) -> str:
    """Render a single result."""

    if output_format == "json":
        return result.model_dump_json(indent=2)
    if output_format == "text":
        return result.text
    if output_format == "markdown":
        return render_markdown(result)
    raise ValueError(f"Unsupported output format: {output_format}")


def render_results(results: list[DocumentResult], *, output_format: OutputFormat) -> str:
    """Render one or more results."""

    if len(results) == 1:
        return render_result(results[0], output_format=output_format)
    if output_format == "json":
        return json.dumps([result.model_dump(mode="json") for result in results], indent=2)
    return "\n\n---\n\n".join(render_result(result, output_format=output_format) for result in results)


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

