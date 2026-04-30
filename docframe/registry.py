"""Adapter registry and base protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from .models import DocumentResult, ProcessingOptions


class DocumentAdapter(ABC):
    """Base class for document adapters."""

    extensions: frozenset[str] = frozenset()

    def supports(self, path: Path) -> bool:
        """Return whether this adapter can process the path."""

        return path.suffix.lower() in self.extensions

    @abstractmethod
    def process(self, path: Path, options: ProcessingOptions) -> DocumentResult:
        """Process a local document into normalized chunks."""


class AdapterRegistry:
    """Registry that maps files to document adapters."""

    def __init__(self) -> None:
        self._adapters: list[DocumentAdapter] = []

    def register(self, adapter: DocumentAdapter) -> None:
        """Register an adapter, replacing an adapter of the same class."""

        self._adapters = [
            existing for existing in self._adapters if existing.__class__ is not adapter.__class__
        ]
        self._adapters.append(adapter)

    def adapter_for(self, path: Path) -> DocumentAdapter:
        """Return the first adapter that supports the path."""

        for adapter in self._adapters:
            if adapter.supports(path):
                return adapter
        raise ValueError(f"No DocFrame adapter registered for {path.suffix or path.name!r}.")

    def supported_extensions(self) -> list[str]:
        """Return all registered file extensions."""

        return sorted({extension for adapter in self._adapters for extension in adapter.extensions})

