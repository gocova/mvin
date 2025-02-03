import sys
sys.path.append('src')

import pytest # required for pytest.raises

from mvin import Token, BaseToken, TokenBool, TokenError, TokenErrorTypes, TokenNumber, TokenString
from mvin.interpreter import get_interpreter

def test_abstractToken():
    with pytest.raises(TypeError):
        base = Token() # pyright: ignore


def test_get_interpreter_ok():
    tokens = [TokenBool(True)]
    run = get_interpreter(tokens)
    assert run is not None

def test_single_bool_ok():
    tokens = [TokenBool(True)]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({})

def test_single_text_ok():
    tokens = [TokenString("hi")]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == "hi"

def test_single_text_neq_1():
    tokens = [TokenString("hi")]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) != 1

def test_single_number():
    tokens = [TokenNumber(1)]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == 1

def test_error_ok():
    error_token = TokenError(TokenErrorTypes.GETTING_DATA, "As expected")
    tokens = [error_token]
    run = get_interpreter(tokens)
    assert run is not None
    result = run({})
    assert result == "#GETTING_DATA"
    assert error_token.message == "As expected"

class ManualToken(BaseToken):
    def __init__(self, value, type, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = type
        self._subtype = subtype

def test_range_missing_args():
    tokens = [ManualToken('F7', 'OPERAND', 'RANGE')]
    run = get_interpreter(tokens)
    assert run is not None
    with pytest.raises(KeyError):
        _ = run({})

def test_range_proper_value_transfer():
    tokens = [ManualToken('F7', 'OPERAND', 'RANGE')]
    run = get_interpreter(tokens)
    assert run is not None
    result = run({"F7": TokenString("done")})
    assert result == "done"

def test_none_as_token():
    tokens = [None]
    with pytest.raises(SyntaxError):
        get_interpreter(tokens) # pyright: ignore

def test_none_as_list():
    run_as_none = get_interpreter(None) # pyright: ignore
    assert run_as_none is None

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
    # with pytest.raises(SyntaxError) as exc_info:


    # assert str(exc_info.value) == "Function `NOT(` expects 1 arguments but got 0."

def test_excel_not_func_ok_result():
    tokens = [ManualToken("NOT(", "FUNC", "OPEN"), TokenBool(True), ManualToken(")", "FUNC", "CLOSE")]
    f = get_interpreter(tokens)
    assert f is not None
    assert not f({})


def test_double_close():
    tokens = [ManualToken("(", "PAREN", "OPEN"), ManualToken(")", "PAREN", "CLOSE"), ManualToken(")", "PAREN", "CLOSE")]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)

    assert str(exc_info.value) == "Unexpected `)` at position 2 (too many closing parentheses)."

def test_operator_after_open():
    tokens = [ManualToken("(", "PAREN", "OPEN"), ManualToken("+", "OPERATOR-INFIX", ""), ManualToken(")", "PAREN", "CLOSE")]
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
        ManualToken(")", "FUNC", "CLOSE")
    ]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)

    assert str(exc_info.value) == "Function `NOT(` expects 1 arguments but got 2."

def test_handle_missing_argument():
    tokens = [
        ManualToken("NOT(", "FUNC", "OPEN"),
        ManualToken(",", "SEP", "ARG"),
        ManualToken(")", "FUNC", "CLOSE")
    ]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)

    assert str(exc_info.value) == "Function `NOT(` expects 1 arguments but got 2."

def test_handle_WSPACE():
    tokens = [
        ManualToken("", "WHITE-SPACE", "")
        , TokenBool(True)
    ]
    f = get_interpreter(tokens)
    assert f is not None

    assert f({})

def test_raise_unrecognized_token():
    tokens = [
        ManualToken("XX", "OPERATOR", ""),
    ]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)

    assert str(exc_info.value) == "Unrecognized token `Token<v:XX t:OPERATOR s: >` at position 0."

def test_raise_unmatched_par():
    tokens = [
        ManualToken("(", "PAREN", "OPEN"), # First (
    ]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)

    assert str(exc_info.value) == "Unmatched `(` (missing closing parenthesis)."

def test_raise_missing_operator_before_open_par():
    tokens = [
        TokenNumber(2),
        ManualToken("(", "PAREN", "OPEN"),
    ]
    with pytest.raises(SyntaxError) as exc_info:
        get_interpreter(tokens)

    assert str(exc_info.value) == "Missing operator before '(' at position 1."

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
    """
    Searching 25 inside 2
    """
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
    tokens = [
        TokenNumber(0),
        TokenNumber(1)
    ]
    f = get_interpreter(tokens)
    assert f is not None
    with pytest.raises(ValueError) as exc_info:
        f({})
    assert str(exc_info.value) == 'Formula evaluation error: too many values remaining.'

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
    assert str(exc_info.value) == 'Function `SEARCH(` expects 3 arguments but got 4.'

def test_double_open_par():
    tokens = [
        TokenNumber(0),
        ManualToken("+", "OPERATOR-INFIX", ""),

    ]
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
