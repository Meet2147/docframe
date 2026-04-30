# DocFrame

DocFrame is a Python framework for turning messy enterprise documents into
structured, AI-ready chunks.

It gives developers one API and one CLI for PDFs, DOCX files, CSVs, Excel
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

Local development:

```bash
python3 -m pip install -e .
```

Then:

```bash
docframe formats
docframe process examples/sample.csv --format markdown
```

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

## Supported Formats

- PDF: text and page metadata via `pypdf`
- DOCX: paragraphs and tables via `python-docx`
- CSV: table chunks via Python's standard `csv` parser
- XLSX/XLSM: worksheet tables via `openpyxl`
- JPG/JPEG/PNG: image metadata via `Pillow`

Images currently emit image chunks and metadata. OCR is intentionally a provider
extension point so teams can choose local OCR, cloud OCR, or multimodal AI.

## Core Concepts

- `DocFrame`: framework object for processing documents
- `DocumentAdapter`: parser for a file family
- `AdapterRegistry`: maps file extensions to adapters
- `DocumentResult`: normalized output for one document
- `DocumentChunk`: text, table, image, or metadata unit
- `Pipeline`: ordered post-processing steps
- `ProcessingOptions`: runtime limits for large files

## CLI

```bash
docframe process FILE_OR_DIRECTORY
docframe process FILE_OR_DIRECTORY --format markdown
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
