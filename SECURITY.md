# Security Policy

DocFrame is currently public-alpha software. Do not use it for regulated or
highly sensitive production workloads until your team has reviewed the parser
surface, dependency chain, sandboxing model, and data-retention behavior.

## Reporting

Please report suspected security issues privately to the project maintainer.
Do not open a public issue with exploit details.

## Parser Safety Notes

- Treat all user-provided documents as untrusted input.
- Run document processing in an isolated worker for multi-tenant deployments.
- Apply file size, page count, row count, and time limits before processing.
- Keep parser dependencies patched.
- Avoid logging extracted document content unless explicitly required.

