# Public Alpha Readiness

DocFrame is ready to publish as a public alpha, not as a production-guaranteed
1.0 framework.

## Ready

- Framework-native CLI: `docframe process ...`
- Python SDK: `DocFrame`, adapters, registry, pipeline, typed results
- Supported formats: PDF, DOC/DOCX, CSV, XLSX/XLSM, JPG/JPEG, PNG
- Pydantic result models and JSON/Markdown/Text output
- Static landing site
- Render static-site Blueprint
- MIT license
- Security notes
- Automated tests for core adapters
- Local private-corpus validator for release gates
- GitHub Actions CI and Pages deployment workflows

## Before Calling It Production Ready

- Add Windows and macOS CI lanes
- Add fuzz/regression corpus for malformed documents
- Add parser sandboxing guidance and timeout enforcement
- Promote corpus validation into CI with a sanitized public fixture set
- Add structured logging and metrics hooks
- Add versioned API compatibility policy
- Add full documentation site with tutorials and extension guides
- Add signed releases and dependency vulnerability scanning
