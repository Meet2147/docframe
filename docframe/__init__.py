"""DocFrame public SDK.

DocFrame is a Python framework for normalizing messy enterprise documents into
typed chunks that can feed search, extraction, review, and AI pipelines.
"""

from .adapters import (
    CsvAdapter,
    DocxAdapter,
    ExcelAdapter,
    ImageAdapter,
    LegacyDocAdapter,
    PdfAdapter,
    adapter_registry,
)
from .core import DocFrame, Pipeline, PipelineStep, process_file
from .models import (
    DocumentChunk,
    DocumentMetadata,
    DocumentResult,
    DocumentType,
    ProcessingOptions,
)
from .registry import AdapterRegistry, DocumentAdapter

__all__ = [
    "AdapterRegistry",
    "CsvAdapter",
    "DocFrame",
    "DocumentAdapter",
    "DocumentChunk",
    "DocumentMetadata",
    "DocumentResult",
    "DocumentType",
    "DocxAdapter",
    "ExcelAdapter",
    "ImageAdapter",
    "LegacyDocAdapter",
    "PdfAdapter",
    "Pipeline",
    "PipelineStep",
    "ProcessingOptions",
    "adapter_registry",
    "process_file",
]
