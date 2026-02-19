# mvin: Minimum Viable Interpreter for Excel Formulas

[![PyPI Version](https://img.shields.io/pypi/v/mvin.svg)](https://pypi.org/project/mvin/)
[![License](https://img.shields.io/badge/License-MIT%20%2F%20Apache%202.0-green.svg)](https://opensource.org/licenses/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/gocova/mvin)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support-orange?logo=buy-me-a-coffee&style=flat-square)](https://buymeacoffee.com/gocova)


`mvin` is a lightweight, dependency-free interpreter for evaluating single Excel-like formulas from
tokenized input. It is built around a shunting-yard parser with a small, extensible
function/operator surface.

If this library saved your team hours of manual formatting, consider buying me a coffee! ☕
Donations help prioritize support for new Excel formulas and complex CSS mapping.

## Why mvin

- No runtime dependencies.
- Works with tokenizer output (for example, `openpyxl` tokens).
- Supports numeric, comparison, and string-concatenation operators.
- Supports unary prefix operators (`+x`, `-x`).
- Allows custom function maps and operator maps.
- Dual licensed under MIT or Apache-2.0.

## Installation

```bash
pip install mvin
```

Python support: `>=3.9,<4.0`.

## Quick Start

```python
from mvin import TokenNumber, TokenOperator
from mvin.interpreter import get_interpreter

tokens = [
    TokenNumber(1),
    TokenOperator("+"),
    TokenNumber(2),
]

run = get_interpreter(tokens)
result = run({}) if run else None
assert result == 3
```

`get_interpreter(...)` returns a callable that evaluates the expression. Inputs for cell references
are passed as a dictionary.

## Token Contract

`mvin` accepts any token object with these attributes:

- `type: str`
- `subtype: str`
- `value: Any`

Built-in token classes are available in `mvin` (`TokenNumber`, `TokenString`, `TokenBool`,
`TokenOperator`, etc.), but third-party tokenizers are supported if they follow the same shape.

## Supported Operators

| Operator | Meaning |
| --- | --- |
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `^` | Exponentiation |
| `&` | String concatenation |
| `=` / `==` | Equality |
| `<>` / `!=` | Inequality |
| `<` | Less than |
| `<=` | Less than or equal |
| `>` | Greater than |
| `>=` | Greater than or equal |
| `+x` | Unary plus (prefix) |
| `-x` | Unary minus (prefix) |

## Built-in Functions

Built-ins are defined in `DEFAULT_FUNCTIONS` in `src/mvin/functions/excel_lib.py`.

| Function | Notes |
| --- | --- |
| `NOT(value)` | Accepts logical or numeric values. |
| `ISERROR(value)` | Returns whether value is an error token. |
| `SEARCH(find_text, within_text, [start_num])` | 1-based index; defaults `start_num` to `1`. |
| `LEFT(text, [num_chars])` | Defaults `num_chars` to `1`. |
| `RIGHT(text, [num_chars])` | Defaults `num_chars` to `1`. |
| `LEN(text)` | Length of text representation. |

## Working with References (Ranges)

If a token has `type="OPERAND"` and `subtype="RANGE"`, its `value` is treated as an input key.

- Required keys are exposed as `run.inputs`.
- Inputs should map reference name to token objects.

```python
from mvin import BaseToken, TokenNumber
from mvin.interpreter import get_interpreter


class RefToken(BaseToken):
    def __init__(self, ref: str):
        super().__init__()
        self._value = ref
        self._type = "OPERAND"
        self._subtype = "RANGE"


tokens = [RefToken("A1")]
run = get_interpreter(tokens)
assert run is not None
assert run.inputs == {"A1"}
assert run({"A1": TokenNumber(10)}) == 10
```

## Customizing Functions

Pass a custom function map through `proposed_functions`.
Function keys follow tokenizer function-open values (for example, `"MYFUNC("`).

```python
from mvin import BaseToken, TokenNumber
from mvin.interpreter import get_interpreter
from mvin.functions.excel_lib import DEFAULT_FUNCTIONS


class T(BaseToken):
    def __init__(self, value: str, token_type: str, subtype: str):
        super().__init__()
        self._value = value
        self._type = token_type
        self._subtype = subtype


def excel_double(value):
    if value is not None and value.type == "OPERAND" and value.subtype == "NUMBER":
        return TokenNumber(value.value * 2)
    return value


custom_functions = dict(DEFAULT_FUNCTIONS)
custom_functions["DOUBLE("] = ([None], excel_double)

tokens = [
    T("DOUBLE(", "FUNC", "OPEN"),
    TokenNumber(21),
    T(")", "FUNC", "CLOSE"),
]

run = get_interpreter(tokens, proposed_functions=custom_functions)
assert run is not None
assert run({}) == 42
```

## Public API Stability

`mvin` follows semantic versioning.

- Patch: bug fixes only.
- Minor: backward-compatible features.
- Major: breaking API changes.

Public API guarantees are documented in `API_STABILITY.md`.

## Development

### Setup

```bash
pdm install -G dev
```

### Run tests

```bash
pdm run pytest -q
```

### Run lint + types

```bash
pdm run ruff check src tests
pdm run mypy
```

### Build

```bash
pdm build
```

### CI/CD

GitHub Actions workflows in `.github/workflows/ci.yml` and `.github/workflows/release.yml` run:

- tests on Python 3.9-3.13
- lint + type checks
- build + `twine check`
- wheel smoke test

Tag pushes matching `v*` also publish to PyPI using Trusted Publishing (GitHub OIDC).

## Contributing and Security

- Contribution guide: `CONTRIBUTING.md`
- Security policy: `SECURITY.md`
- Release checklist: `RELEASE.md`
- Changelog: `CHANGELOG.md`

## License

Licensed under either of:

- Apache License, Version 2.0 ([`LICENSE_APACHE`](LICENSE_APACHE) or
  <https://www.apache.org/licenses/LICENSE-2.0>)
- MIT license ([`LICENSE_MIT`](LICENSE_MIT) or <https://opensource.org/licenses/MIT>)

at your option.
