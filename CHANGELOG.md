# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]

### Added

- Bitbucket Pipelines CI/CD with multi-version tests, lint/type checks, build checks, and PyPI
  publishing on `v*` tags.
- Unary prefix operator support (`+x`, `-x`) in the interpreter.
- Property-based parser tests with Hypothesis.
- API stability policy (`API_STABILITY.md`), contributing, security, and release docs.
- Typed package marker (`py.typed`).

### Changed

- Switched project metadata and workflows to a PDM-first release setup.
- Added explicit public API exports (`__all__`) in `mvin`.
- Moved version management to SCM-driven dynamic versioning via PDM.

### Fixed

- `RIGHT(text, 0)` now returns an empty string.
- `SEARCH`, `LEFT`, and `RIGHT` reject non-integer numeric arguments with tokenized errors.
- Falsey custom tokens are no longer misclassified as missing values.
- Function results are kept when they are valid falsey tokens.
- Comma separators outside function calls now raise syntax errors during parsing.
