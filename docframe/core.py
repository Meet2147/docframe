"""DocFrame processing engine and pipeline API."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable, Iterable
from pathlib import Path
from typing import TypeAlias

from .adapters import adapter_registry
from .models import DocumentResult, ProcessingOptions
from .registry import AdapterRegistry, DocumentAdapter
from .utils import build_metadata

PipelineStep: TypeAlias = Callable[[DocumentResult], DocumentResult | Awaitable[DocumentResult]]


class Pipeline:
    """Composable post-processing pipeline for normalized document results."""

    def __init__(self) -> None:
        self._steps: list[PipelineStep] = []

    def use(self, step: PipelineStep) -> "Pipeline":
        """Register a step and return self for fluent composition."""

        self._steps.append(step)
        return self

    async def run(self, result: DocumentResult) -> DocumentResult:
        """Run all registered steps in order."""

        current = result
        for step in self._steps:
            maybe_result = step(current)
            current = await maybe_result if inspect.isawaitable(maybe_result) else maybe_result
        return current


class DocFrame:
    """Framework object for document normalization and processing pipelines."""

    def __init__(
        self,
        *,
        options: ProcessingOptions | None = None,
        registry: AdapterRegistry | None = None,
        pipeline: Pipeline | None = None,
    ) -> None:
        self.options = options or ProcessingOptions()
        self.registry = registry or adapter_registry()
        self.pipeline = pipeline or Pipeline()

    def register_adapter(self, adapter: DocumentAdapter) -> None:
        """Register or replace an adapter."""

        self.registry.register(adapter)

    def use(self, step: PipelineStep) -> "DocFrame":
        """Register a pipeline step."""

        self.pipeline.use(step)
        return self

    async def process(self, path: str | Path) -> DocumentResult:
        """Process one document asynchronously."""

        file_path = Path(path).expanduser().resolve()
        adapter = self.registry.adapter_for(file_path)
        result = await asyncio.to_thread(adapter.process, file_path, self.options)
        return await self.pipeline.run(result)

    async def process_safe(self, path: str | Path) -> DocumentResult:
        """Process one document and return parser failures as structured errors."""

        file_path = Path(path).expanduser().resolve()
        try:
            return await self.process(file_path)
        except Exception as exc:
            metadata = build_metadata(file_path)
            return DocumentResult(
                document_id=metadata.sha256,
                metadata=metadata,
                chunks=[],
                errors=[f"{type(exc).__name__}: {exc}"],
            )

    async def process_many(
        self,
        paths: Iterable[str | Path],
        *,
        continue_on_error: bool = False,
    ) -> list[DocumentResult]:
        """Process many documents concurrently.

        Set ``continue_on_error`` for corpus/batch jobs where one malformed file
        should not fail the whole run.
        """

        processor = self.process_safe if continue_on_error else self.process
        semaphore = asyncio.Semaphore(self.options.max_concurrency)

        async def bounded_process(path: str | Path) -> DocumentResult:
            async with semaphore:
                return await processor(path)

        return await asyncio.gather(*(bounded_process(path) for path in paths))

    def process_sync(self, path: str | Path) -> DocumentResult:
        """Process one document from synchronous Python code."""

        return asyncio.run(self.process(path))


def process_file(path: str | Path, *, options: ProcessingOptions | None = None) -> DocumentResult:
    """Convenience function for synchronous one-file processing."""

    return DocFrame(options=options).process_sync(path)
