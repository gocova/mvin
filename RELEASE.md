# Release Checklist (PDM + GitHub)

## 1. Pre-release

- Ensure `CHANGELOG.md` is updated.
- Run local gates:

```bash
pdm install -G dev
pdm run pytest -q
pdm run ruff check src tests
pdm run mypy
pdm build
pdm run twine check dist/*
```

## 2. Tag and Push

- Create an annotated tag with semver format:

```bash
git tag -a vX.Y.Z -m "mvin vX.Y.Z"
git push origin vX.Y.Z
```

## 3. CI Publish

- GitHub Actions release workflow for `v*` tags runs build + publish.
- Configure repository secret:
  - `PYPI_API_TOKEN`: PyPI token with publish scope for `mvin`.

## 4. Post-release

- Confirm release on PyPI.
- Verify install:

```bash
pip install --upgrade mvin
python -c "import mvin; print(mvin.__version__)"
```

- Announce release notes from `CHANGELOG.md`.
