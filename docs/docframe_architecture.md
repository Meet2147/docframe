# DocFrame Architecture

DocFrame is a document-processing framework for PDFs, DOCX files, CSVs, Excel
workbooks, and images. The long-term vision is a single developer API for
enterprise document normalization, extraction, indexing, and AI workflows.

## Developer Experience

```bash
docframe process contract.pdf --format markdown
docframe process ./inbox --recursive --out normalized.json
python -m docframe process report.xlsx
```

Python API:

```python
import docframe as df

framework = df.DocFrame()
result = framework.process_sync("report.docx")
print(result.text)
```

## Core Concepts

- `DocumentAdapter`: parser for one family of formats.
- `AdapterRegistry`: maps files to adapters.
- `DocumentResult`: normalized output for one document.
- `DocumentChunk`: text, table, image, or metadata unit.
- `Pipeline`: ordered post-processing steps over normalized results.
- `ProcessingOptions`: extraction limits for large files.
- `process_many(..., continue_on_error=True)`: safe corpus mode that returns
  per-file parser errors instead of failing an entire batch.

## Built-In Adapters

- PDF via `pypdf`
- DOCX via `python-docx`
- CSV via Python `csv`
- XLSX/XLSM via `openpyxl`
- JPG/PNG via `Pillow`

Images currently emit metadata and image chunks. OCR is deliberately an
extension point so DocFrame can support local OCR, cloud OCR, or multimodal AI
providers without hard-coding one vendor.
