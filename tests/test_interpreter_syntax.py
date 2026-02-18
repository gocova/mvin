import sys

sys.path.append("src")

import pytest  # required for pytest.raises

from mvin import BaseToken, TokenBool, TokenNumber, TokenString
from mvin.interpreter import get_interpreter


class ManualToken(BaseToken):
    def __init__(self, value, token_type, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = token_type
        self._subtype = subtype


def test_incomplete_call():
    tokens = [ManualToken("SEARCH(", "FUNC", "OPEN")]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert str(exc_info.value) == "Unmatched `(` (missing closing parenthesis)."


def test_non_existing_func():
    tokens = [ManualToken("ROBIN(", "FUNC", "OPEN"), ManualToken(")", "FUNC", "CLOSE")]
    with pytest.raises(SyntaxError):
        get_interpreter(tokens)


def test_excel_not_func_incomplete_call():
    tokens = [ManualToken("NOT(", "FUNC", "OPEN"), ManualToken(")", "FUNC", "CLOSE")]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert str(exc_info.value) == "Missing required argument at 0 for function `NOT(`"


def test_double_close():
    tokens = [
        ManualToken("(", "PAREN", "OPEN"),
        ManualToken(")", "PAREN", "CLOSE"),
        ManualToken(")", "PAREN", "CLOSE"),
    ]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert str(exc_info.value) == "Unexpected `)` at position 2 (too many closing parentheses)."


def test_operator_after_open():
    tokens = [
        ManualToken("(", "PAREN", "OPEN"),
        ManualToken("+", "OPERATOR-INFIX", ""),
        ManualToken(")", "PAREN", "CLOSE"),
    ]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert str(exc_info.value) == "Unexpected operator `Token<v:+ t:OPERATOR-INFIX s: >` at position 1."


def test_missing_operator_before_par():
    tokens = [TokenNumber(2), ManualToken("(", "PAREN", "OPEN")]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert str(exc_info.value) == "Missing operator before '(' at position 1."


def test_handle_missing_last_argument():
    tokens = [
        ManualToken("NOT(", "FUNC", "OPEN"),
        TokenBool(True),
        ManualToken(",", "SEP", "ARG"),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert str(exc_info.value) == "Function `NOT(` expects 1 arguments but got 2."


def test_handle_missing_argument():
    tokens = [
        ManualToken("NOT(", "FUNC", "OPEN"),
        ManualToken(",", "SEP", "ARG"),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert str(exc_info.value) == "Function `NOT(` expects 1 arguments but got 2."


def test_handle_WSPACE():
    tokens = [ManualToken("", "WHITE-SPACE", ""), TokenBool(True)]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({})


def test_raise_unrecognized_token():
    tokens = [ManualToken("XX", "OPERATOR", "")]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert str(exc_info.value) == "Unrecognized token `Token<v:XX t:OPERATOR s: >` at position 0."


def test_raise_unmatched_par():
    tokens = [ManualToken("(", "PAREN", "OPEN")]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert str(exc_info.value) == "Unmatched `(` (missing closing parenthesis)."


def test_raise_missing_operator_before_open_par():
    tokens = [TokenNumber(2), ManualToken("(", "PAREN", "OPEN")]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert str(exc_info.value) == "Missing operator before '(' at position 1."


def test_too_many_args():
    tokens = [
        ManualToken("SEARCH(", "FUNC", "OPEN"),
        TokenString("hi"),
        ManualToken(",", "SEP", "ARG"),
        TokenString("hi world"),
        ManualToken(",", "SEP", "ARG"),
        TokenNumber(1),
        ManualToken(",", "SEP", "ARG"),
        TokenNumber(1),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert str(exc_info.value) == "Function `SEARCH(` expects 3 arguments but got 4."


def test_separator_outside_function_is_rejected():
    tokens = [
        ManualToken("(", "PAREN", "OPEN"),
        TokenNumber(1),
        ManualToken(",", "SEP", "ARG"),
        TokenNumber(2),
        ManualToken(")", "PAREN", "CLOSE"),
    ]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)
    assert (
        str(exc_info.value)
        == "Unexpected separator `Token<v:, t:SEP s:ARG >` at position 2."
    )
