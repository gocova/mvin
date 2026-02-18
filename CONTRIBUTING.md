# Contributing

## Development Setup

```bash
pdm install -G dev
```

## Local Quality Gates

Run all of these before opening a pull request:

```bash
pdm run pytest -q
pdm run ruff check src tests
pdm run mypy
pdm build
pdm run twine check dist/*
```

## Branch and PR Expectations

- Keep pull requests focused and small.
- Add or update tests for behavior changes.
- Update `CHANGELOG.md` for user-visible changes.
- Do not commit generated artifacts (`dist/`, `*.egg-info/`, caches).

## Versioning

- The project version is SCM/tag-driven through PDM.
- Use tags like `vX.Y.Z` for stable releases and `vX.Y.ZrcN` for release candidates.
