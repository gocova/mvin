# 📄 mvin: Minimum Viable Interpreter for Excel Formulas

[![PyPI Version](https://img.shields.io/pypi/v/mvin.svg)](https://pypi.org/project/mvin/)
[![License](https://img.shields.io/badge/License-MIT%20%2F%20Apache%202.0-green.svg)](https://opensource.org/licenses/)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support%20the%20Project-orange?logo=buy-me-a-coffee&style=flat-square)](https://buymeacoffee.com/gocova)

**mvin** is a lightweight, dependency-free interpreter for evaluating single Excel formulas. Built on a **modified Dijkstra’s shunting yard algorithm**, it supports extendable operator and function libraries, allowing customization without modifying the core codebase.

`Mvin` is designed to be **simple, efficient, and easily extendable** Excel's formulas interpreter under a permissive **MIT or Apache 2.0 license**.
<a href="https://www.buymeacoffee.com/gocova" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-violet.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

---

## ✨ Features

- **🚀 Lightweight & No Dependencies** – Works out-of-the-box.
- **🔌 Extendable Functions & Operators** – Easily add new logic.
- **🧵 Thread-Safe Design** – Safe for concurrent execution (needs validation).
- **📜 Tokenizer-Agnostic** – Works with `openpyxl` and other tokenizers.
- **📂 Simple Licensing** – MIT or Apache 2.0.

---

## 📦 Installation

You can install `mvin` via **PyPI**:

```sh
pip install mvin
```

## 🚀 Usage

### Basic Formula Evaluation

To use mvin, you need a tokenizer that returns tokens with the following properties:
* type (string)
* subtype (string)
* value (any)

A predefined set of tokens is available in the module, but you can also use openpyxl for tokenization.

```python
tokens = [TokenNumber(1), TokenOperator("+"), TokenNumber(2)]
callable_f = get_interpreter(tokens)
if callable_f is not None:
    result = callable_f({}) # Calling with empty reference/value dictionary
    # result = 3
```

---

## 💡 Use Cases & Examples

mvin is designed for lightweight, extendable Excel formula evaluation, making it ideal for various scenarios. Here are some common use cases:

### 1. Conditional Formatting Evaluations --> Automate rules outside of Excel.

Since mvin was originally built as the core interpreter for condif2css (to be released), it excels at evaluating conditions used in Excel’s conditional formatting.

### 2. Simple Data Validation Rules --> Validate form inputs, API data, or CSV file contents.

mvin can be used to apply spreadsheet-style validation to incoming data.

### 3. Lightweight Formula Evaluation in Applications --> Implement simple Excel formula support in a web app or database.

If you need Excel-like formula evaluation but don’t want to depend on a full workbook engine like formulas or xlcalculator, mvin offers a minimalist alternative.

---

## 📖 Supported Operators & Functions

### Operators

The mvin interpreter supports a comprehensive set of numeric and comparison operators:

#### Arithmetic Operators

<table>
	<thead>
		<th>Operator</td>
		<th>Description</td>
	</thead>
	<tbody>
		<tr>
			<td>+</td>
			<td>Addition</td>
		</tr>
		<tr>
			<td>-</td>
			<td>Substraction</td>
		</tr>
		<tr><td>*</td><td>Multiplication</td></tr>
		<tr><td>/</td><td>Division</td></tr>
		<tr><td>^</td><td>Exponentiation</td></tr>
	</tbody>
</table>

#### Logical Operators

<table>
	<thead>
		<tr>
			<th>Operator</th>
			<th>Description</th>
		</tr>
	</thead>
	<tbody>
		<tr><td>=</td><td>Equal to</td></tr>
		<tr><td>!=</td><td>Not equal to</td></tr>
		<tr><td>&lt;&gt;</td><td>Not equal to (alternative notation)</td></tr>
		<tr><td>&gt;</td><td>Greater than</td></tr>
		<tr><td>&gt;=</td><td>Greater than or equal to
		<tr>
			<td>&lt;</td><td>Less than</td>
		</tr>
		<tr>
			<td>&lt;=</td><td>Less than or equal to</td>
		</tr>
	</tbody>
</table>

### 📌 Built-in Functions

Unlike full-fledged Excel formula interpreters, mvin includes only a minimal set of built-in functions, as it was originally designed for conditional formatting evaluation:

<table>
	<thead>
		<tr>
			<th>Function</th>
			<th>Description</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>NOT(value)</td>
			<td>Returns the logical negation of a boolean value.</td>
		</tr>
		<tr>
			<td>ISERROR(value)</td>
			<td>Returns TRUE if the given value represents an error.</td>
		</tr>
		<tr>
			<td>SEARCH(substring, text, [start])</td>
			<td>Finds the position of substring within text, optionally starting from start index.</td>
		</tr>
	</tbody>
</table>

For more advanced use cases, users can extend the function library by passing a custom dictionary of functions to the interpreter.

---

## ⚠️ Limitations & Roadmap

### Current Limitations

*	Limited Built-in Functions – Only NOT, ISERROR, and SEARCH are available. Users must define additional functions as needed.
*	No Direct Workbook Integration – Unlike formulas, mvin does not evaluate references across sheets or workbooks.
*	No Built-in Tokenizer – Requires an external tokenizer (e.g., openpyxl) to process formulas.

### Planned Enhancements

* Improved Function Library – More Excel-like functions such as IF, AND, and OR may be added in future versions.
* Thread-Safety Validation – While designed for thread safety, formal testing is needed.

---

## 🛠️ Testing & Code Coverage

mvin includes a comprehensive test suite with 93% test coverage.

To run the tests, use:

```sh
pytest tests/
```

If you contribute to mvin, please ensure your changes do not reduce coverage.

---

## ⚖️ Comparison with Other Excel Interpreters

<table>
<thead><tr><th>Feature</th><th>mvin</th><th>formulas</th><th>xlcalculator</th></tr></thead>
<tbody>
<tr><td>License</td><td>MIT / Apache 2.0</td><td>GPL-3.0</td><td>MIT</td></tr>
<tr><td>Dependencies</td><td>None</td><td>Pandas, NumPy</td><td>NumPy, OpenPyXL</td></tr>
<tr><td>Function Support</td><td>Minimal (NOT, ISERROR, SEARCH)</td><td>Extensive</td><td>Extensive</td></tr>
<tr><td>Operators</td><td>Arithmetic & Comparisons</td><td>Arithmetic & Logical</td><td>Arithmetic & Logical</td></tr>
<tr><td>Thread Safe</td><td>Potentially (Not Tested)</td><td>❌</td><td>✅</td></tr>
<tr><td>Tokenizer Required?</td><td>Yes (e.g., OpenPyXL)</td><td>No</td><td>No</td></tr>
<tr><td>Designed for</td><td>Conditional Formatting</td><td>Full Workbook</td><td>Full Workbook</td></tr>
</tbody>
</table>

mvin is ideal for lightweight, extendable formula evaluation, particularly in scenarios like conditional formatting where a full Excel engine is unnecessary.

---

## 📜 Changelog & Versioning

Version 0.5.0b2 (Initial Release)

🚀 First public release of mvin with the following features:

- Supports numeric and comparison operators: +, -, *, /, ^, =, !=, <>, >, >=, <, <=.
- Minimal built-in function set: NOT, ISERROR, SEARCH.
- Extendable architecture: Custom operators and functions.
- Tokenizer-agnostic design: Requires an external tokenizer.
- No dependencies: Pure Python implementation.
- Designed for conditional formatting: Built for condif2css.

Future releases will focus on:

- Adding more built-in functions (IF, AND, OR, etc.).
- Thread-safety validation.

---

## License

mvin is licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
  <https://www.apache.org/licenses/LICENSE-2.0>)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or <https://opensource.org/licenses/MIT>)

at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in mvin
by you, as defined in the Apache-2.0 license, shall be dually licensed as above, without any
additional terms or conditions.
