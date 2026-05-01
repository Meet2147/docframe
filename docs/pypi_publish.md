# Publishing `docframe-ai` To PyPI

DocFrame is published to PyPI as `docframe-ai` while keeping the Python import
name as `docframe`.

## PyPI Trusted Publisher

Create a PyPI pending publisher with these GitHub settings:

```text
PyPI Project Name: docframe-ai
Owner: Meet2147
Repository name: docframe
Workflow name: publish.yml
Environment name: pypi
```

The workflow lives at `.github/workflows/publish.yml` and uses PyPI Trusted
Publishing, so no PyPI API token is stored in GitHub.

## First Release

After the pending publisher is created in PyPI:

1. Go to GitHub Actions.
2. Open the `Publish to PyPI` workflow.
3. Click `Run workflow`.
4. Confirm PyPI created `docframe-ai`.

After that, normal releases can be published by creating a GitHub release.

## Install

```bash
python3 -m pip install docframe-ai
```

Then:

```python
import docframe as df
```
