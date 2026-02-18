import pytest  # required for pytest.raises

from mvin import BaseToken, TokenBool, TokenNumber, TokenParen, TokenString
from mvin.interpreter import get_interpreter


class ManualToken(BaseToken):
    def __init__(self, value, token_type, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = token_type
        self._subtype = subtype


def test_excel_not_func_ok_result():
    tokens = [
        ManualToken("NOT(", "FUNC", "OPEN"),
        TokenBool(True),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert not f({})


def test_multiple_operations():
    tokens = [
        ManualToken("(", "PAREN", "OPEN"),
        TokenNumber(2),
        ManualToken("+", "OPERATOR-INFIX", ""),
        TokenNumber(0),
        ManualToken(")", "PAREN", "CLOSE"),
        ManualToken("*", "OPERATOR-INFIX", ""),
        ManualToken("(", "PAREN", "OPEN"),
        TokenNumber(10),
        ManualToken("+", "OPERATOR-INFIX", ""),
        TokenNumber(2),
        ManualToken("^", "OPERATOR-INFIX", ""),
        TokenNumber(3),
        ManualToken(")", "PAREN", "CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({}) == 36


def test_multiple_operations_with_token_paren():
    tokens = [
        TokenParen("OPEN"),
        TokenNumber(2),
        ManualToken("+", "OPERATOR-INFIX", ""),
        TokenNumber(0),
        TokenParen("CLOSE"),
        ManualToken("*", "OPERATOR-INFIX", ""),
        TokenParen("OPEN"),
        TokenNumber(10),
        ManualToken("+", "OPERATOR-INFIX", ""),
        TokenNumber(2),
        ManualToken("^", "OPERATOR-INFIX", ""),
        TokenNumber(3),
        TokenParen("CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({}) == 36


def test_search_with_leading_whitespace_keeps_separator_indexing():
    tokens = [
        ManualToken("", "WHITE-SPACE", ""),
        ManualToken("SEARCH(", "FUNC", "OPEN"),
        TokenString("a"),
        ManualToken(",", "SEP", "ARG"),
        TokenString("abc"),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({}) == 1


def test_complex_search_call_with_warning():
    tokens = [
        TokenNumber(0),
        ManualToken("+", "OPERATOR-INFIX", ""),
        ManualToken("SEARCH(", "FUNC", "OPEN"),
        TokenNumber(1),
        ManualToken("+", "OPERATOR-INFIX", ""),
        TokenNumber(1),
        ManualToken(",", "SEP", "ARG"),
        TokenNumber(5),
        ManualToken("^", "OPERATOR-INFIX", ""),
        TokenNumber(2),
        ManualToken(")", "PAREN", "CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({}) == 1


def test_complex_search_call():
    tokens = [
        TokenNumber(2),
        ManualToken("+", "OPERATOR-INFIX", ""),
        ManualToken("SEARCH(", "FUNC", "OPEN"),
        TokenNumber(1),
        ManualToken("+", "OPERATOR-INFIX", ""),
        TokenNumber(1),
        ManualToken(",", "SEP", "ARG"),
        TokenNumber(5),
        ManualToken("^", "OPERATOR-INFIX", ""),
        TokenNumber(2),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({}) == 3


def test_complex_search_call_returns_not_found():
    tokens = [
        TokenNumber(0),
        ManualToken("+", "OPERATOR-INFIX", ""),
        ManualToken("SEARCH(", "FUNC", "OPEN"),
        TokenNumber(5),
        ManualToken("^", "OPERATOR-INFIX", ""),
        TokenNumber(2),
        ManualToken(",", "SEP", "ARG"),
        TokenNumber(1),
        ManualToken("+", "OPERATOR-INFIX", ""),
        TokenNumber(1),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({}) == "#VALUE!"


def test_incomplete_definition():
    tokens = [TokenNumber(0), TokenNumber(1)]
    f = get_interpreter(tokens)
    assert f is not None
    with pytest.raises(ValueError) as exc_info:
        f({})
    assert str(exc_info.value) == "Formula evaluation error: too many values remaining."


def test_double_open_par():
    tokens = [TokenNumber(0), ManualToken("+", "OPERATOR-INFIX", "")]
    f = get_interpreter(tokens)
    assert f is not None
    with pytest.raises(ValueError) as exc_info:
        f({})
    assert str(exc_info.value) == "Not enough values for operation '+'."


def test_required_missing_args():
    tokens = [
        ManualToken("SEARCH(", "FUNC", "OPEN"),
        TokenNumber(1),
        ManualToken("+", "OPERATOR-INFIX", ""),
        TokenNumber(1),
        ManualToken(",", "SEP", "ARG"),
        ManualToken(",", "SEP", "ARG"),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    with pytest.raises(ValueError) as exc_info:
        f({})
    assert str(exc_info.value) == "Missing required argument at 1 for function `SEARCH(`"


def test_unary_minus_simple():
    tokens = [ManualToken("-", "OPERATOR-PREFIX", ""), TokenNumber(2)]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({}) == -2


def test_unary_minus_after_infix():
    tokens = [
        TokenNumber(1),
        ManualToken("+", "OPERATOR-INFIX", ""),
        ManualToken("-", "OPERATOR-PREFIX", ""),
        TokenNumber(2),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({}) == -1


def test_unary_minus_has_lower_precedence_than_exponent():
    tokens = [
        ManualToken("-", "OPERATOR-PREFIX", ""),
        TokenNumber(2),
        ManualToken("^", "OPERATOR-INFIX", ""),
        TokenNumber(2),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({}) == -4


def test_unary_minus_can_be_exponent_operand():
    tokens = [
        TokenNumber(2),
        ManualToken("^", "OPERATOR-INFIX", ""),
        ManualToken("-", "OPERATOR-PREFIX", ""),
        TokenNumber(2),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({}) == 0.25
