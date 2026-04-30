"""Typed document models emitted by DocFrame adapters."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

DocumentType = Literal["pdf", "docx", "csv", "xlsx", "image", "unknown"]
ChunkType = Literal["text", "table", "image", "metadata"]


class ProcessingOptions(BaseModel):
    """Runtime limits and extraction options for document processing."""

    model_config = ConfigDict(extra="forbid")

    max_chars_per_text_chunk: int = Field(default=20_000, ge=1)
    max_table_rows: int = Field(default=1_000, ge=1)
    include_binary: bool = False
    include_metadata: bool = True


class DocumentMetadata(BaseModel):
    """Normalized metadata for any supported document."""

    model_config = ConfigDict(extra="forbid")

    source_path: str
    filename: str
    extension: str
    document_type: DocumentType
    mime_type: str
    size_bytes: int
    sha256: str
    page_count: int | None = None
    sheet_count: int | None = None
    row_count: int | None = None
    width: int | None = None
    height: int | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    """A normalized unit of document content."""

    model_config = ConfigDict(extra="forbid")

    id: str
    type: ChunkType
    text: str | None = None
    rows: list[dict[str, Any]] | None = None
    page: int | None = None
    sheet: str | None = None
    source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentResult(BaseModel):
    """Complete processed output for one document."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    metadata: DocumentMetadata
    chunks: list[DocumentChunk] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def text(self) -> str:
        """Concatenate text chunks for search, RAG, and previews."""

        return "\n\n".join(chunk.text for chunk in self.chunks if chunk.text)

    @computed_field
    @property
    def table_count(self) -> int:
        """Return the number of table chunks."""

        return sum(1 for chunk in self.chunks if chunk.type == "table")

