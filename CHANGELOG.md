# Changelog

## 0.2.0 - Corpus Hardening

- Renamed the PyPI distribution to `docframe-ai` while keeping the `docframe` import.
- Added bounded concurrency for batch processing and the CLI.
- Added `.doc` support with direct OOXML extraction for misnamed Word packages.
- Added safe metadata-only fallback for true legacy binary `.doc` files.
- Replaced Word extraction with direct `word/document.xml` parsing to avoid loading embedded media.
- Suppressed noisy PDF parser logs while preserving structured per-file errors.
- Added a private corpus validator release gate.
- Validated a 1,495-file local corpus with zero processing errors.

## 0.1.0 - Public Alpha

- Added `docframe process` CLI.
- Added Python API with `DocFrame`, `Pipeline`, adapters, and normalized models.
- Added built-in adapters for PDF, DOCX, CSV, XLSX/XLSM, JPG, JPEG, and PNG.
- Added static marketing site and launch documentation.
- Added tests covering generated CSV, DOCX, XLSX, PDF, and PNG fixtures.
- Added safe batch processing with structured per-file errors.
