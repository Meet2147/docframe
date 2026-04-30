"""DocFrame framework quickstart."""

from __future__ import annotations

import asyncio
from pathlib import Path

import docframe as df


async def main() -> None:
    """Process a document and print a compact summary."""

    framework = df.DocFrame()
    result = await framework.process(Path("examples/sample.csv"))
    print(result.metadata.filename)
    print(result.metadata.document_type)
    print(len(result.chunks))


if __name__ == "__main__":
    asyncio.run(main())

