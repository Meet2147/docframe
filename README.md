# DocFrame

DocFrame is a Python framework for turning messy enterprise documents into
structured, AI-ready chunks.

It gives developers one API and one CLI for PDFs, Word files, CSVs, Excel
workbooks, JPGs, and PNGs.

```bash
docframe process contract.pdf --format markdown
docframe process ./inbox --recursive --out normalized.json
python3 -m docframe process report.xlsx
```

## Why DocFrame

Document workflows usually start with format chaos: text PDFs, scanned images,
spreadsheets, Word files, CSV exports, and ad hoc attachments. DocFrame gives
you a normalized result model so downstream systems can search, extract,
summarize, validate, and route documents without rewriting parsers for every
file type.

## Install

From PyPI:

```bash
python3 -m pip install docframe-ai
```

Local development:

```bash
python3 -m pip install -e .
```

Then:

```bash
docframe formats
docframe process examples/sample.csv --format markdown
```

The PyPI distribution is `docframe-ai`; the Python import remains `docframe`.
See the repository's
[PyPI publishing guide](https://github.com/Meet2147/docframe/blob/main/docs/pypi_publish.md)
for the GitHub Trusted Publishing setup.

## Python API

```python
import docframe as df

framework = df.DocFrame()
result = framework.process_sync("examples/sample.csv")

print(result.metadata.document_type)
print(result.chunks[0].rows)
```

Async processing:

```python
import docframe as df

framework = df.DocFrame()
results = await framework.process_many(["contract.pdf", "report.xlsx"])
```

Safe corpus processing:

```python
import docframe as df

framework = df.DocFrame()
results = await framework.process_many(
    ["good.pdf", "malformed.pdf"],
    continue_on_error=True,
)

for result in results:
    if result.errors:
        print(result.metadata.filename, result.errors)
```

LLM-ready token blocks:

```python
import docframe as df

framework = df.DocFrame()
result = framework.process_sync("report.pdf")

tokens = df.to_llm_tokens(result)
prompt = df.to_llm_prompt(result)
```

From the CLI:

```bash
docframe process report.pdf --format tokens
docframe process ./documents --recursive --format llm --out llm_payload.json
docframe process report.pdf --format prompt --out prompt.txt
```

`tokens` returns a JSON list of source-grounded text blocks. `llm` returns a
compact `docframe.sager.tokens.v1` payload. `prompt` returns plain text ready to
paste or pass directly into an LLM call.

## Supported Formats

- PDF: text and page metadata via `pypdf`
- DOCX: paragraphs and tables via direct OOXML package parsing
- DOC: OOXML extraction when possible, metadata-only fallback for legacy binary Word files
- CSV: table chunks via Python's standard `csv` parser
- XLSX/XLSM: worksheet tables via `openpyxl`
- JPG/JPEG/PNG: image metadata via `Pillow`

Images currently emit image chunks and metadata. OCR is intentionally a provider
extension point so teams can choose local OCR, cloud OCR, or multimodal AI.

Many real corpora contain OOXML Word documents with a `.doc` extension. DocFrame
extracts those with the Word adapter and emits a warning. True legacy binary
`.doc` files emit metadata and a warning; convert them to `.docx` or register a
custom adapter when full text extraction is required.

## Core Concepts

- `DocFrame`: framework object for processing documents
- `DocumentAdapter`: parser for a file family
- `AdapterRegistry`: maps file extensions to adapters
- `DocumentResult`: normalized output for one document
- `DocumentChunk`: text, table, image, or metadata unit
- `Pipeline`: ordered post-processing steps
- `ProcessingOptions`: runtime limits and concurrency controls for large files

## CLI

```bash
docframe process FILE_OR_DIRECTORY
docframe process FILE_OR_DIRECTORY --format markdown
docframe process FILE_OR_DIRECTORY --format tokens
docframe process FILE_OR_DIRECTORY --format llm
docframe process FILE_OR_DIRECTORY --format prompt
docframe process FILE_OR_DIRECTORY --recursive --out normalized.json
docframe formats
```

## Status

DocFrame is **public alpha** software. The core API, adapters, CLI, tests, MIT
license, and landing site are in place. See [PUBLIC_ALPHA.md](PUBLIC_ALPHA.md)
for the production-readiness checklist.

## Verify

```bash
python3 -m unittest discover -s tests
python3 -m compileall docframe tests
```

## Website

The static site lives in [site/index.html](site/index.html).

Run it locally:

```bash
python3 -m http.server 8080 -d site
```

Then open:

```text
http://127.0.0.1:8080/
```

## Deploy Static Site On Render

The repository includes a Render Blueprint in [render.yaml](render.yaml). It
publishes the static site from `site/` as `docframe-site`.

After pushing the repository to GitHub, GitLab, or Bitbucket:

```bash
git push -u origin main
```

Then create the Blueprint from the Render Dashboard:

```text
https://dashboard.render.com/blueprint/new
```

Connect the repository and Render will use `render.yaml` from the repo root.

## Corpus Utilities

Validate a private corpus before a release:

```bash
python3 scripts/validate_corpus.py test_corpus --out corpus-report.json
```

The validator exits nonzero if any supported file produces a structured error.
Use `--allow-errors` for exploratory runs where malformed files are expected.

Collect any supported corpus files by extension:

```bash
python3 scripts/collect_files.py "/path/to/archive" "/path/to/all_csv" --ext csv --dry-run --quiet
python3 scripts/collect_files.py "/path/to/archive" "/path/to/all_csv" --ext csv --quiet
python3 scripts/collect_files.py "/path/to/archive" "/path/to/all_images" --ext jpg --ext png --quiet
```

Collect PDFs from a deeply nested archive into one flat folder:

```bash
python3 scripts/collect_pdfs.py "/path/to/archive" "/path/to/all_pdfs" --dry-run --quiet
python3 scripts/collect_pdfs.py "/path/to/archive" "/path/to/all_pdfs" --quiet
```

The collector copies by default, avoids overwriting existing files, and gives
duplicate basenames a stable hash suffix.
