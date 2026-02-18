# API Stability Policy

`mvin` follows semantic versioning.

## Public Surface

The symbols exported by `mvin.__all__` are the supported public API:

- token classes
- token error types
- operator registration helpers
- `REGISTERED_OPS`
- `__version__`

`mvin.interpreter.get_interpreter` and `mvin.functions.excel_lib.DEFAULT_FUNCTIONS` are also
considered public.

## Compatibility Guarantees

- Patch releases: no breaking API changes.
- Minor releases: backward-compatible API additions and behavior fixes.
- Major releases: breaking changes are allowed and documented in `CHANGELOG.md`.

## Non-public / Internal

Anything not listed above may change without notice, including:

- internal parser helpers
- internal error messages (except where tests explicitly guarantee behavior)
- internal module structure
