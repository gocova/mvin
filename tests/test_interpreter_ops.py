import pytest

from mvin import BaseToken, TokenError, TokenErrorTypes, TokenNumber, TokenOperator, TokenString
from mvin.interpreter import get_interpreter


class ManualToken(BaseToken):
    def __init__(self, value, type, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = type
        self._subtype = subtype

def test_concat_ok():
    tokens = [TokenString("hi "), ManualToken("&", "OPERATOR-INFIX", ""), TokenString("world")]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == "hi world"

def test_concat_left_err():
    tokens = [TokenError(
        TokenErrorTypes.REF, "Undefined message"
    ), ManualToken("&", "OPERATOR-INFIX", ""), TokenString("world")]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == "#REF!"

def test_concat_right_err():
    tokens = [TokenString("hi "), ManualToken("&", "OPERATOR-INFIX", ""), TokenError(
        TokenErrorTypes.REF, "Undefined message"
    )]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == "#REF!"

def test_concat_numeric_ok():
    tokens = [TokenNumber(1), ManualToken("&", "OPERATOR-INFIX", ""), TokenNumber(2)]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == "12"

def test_add_ok():
    tokens = [TokenNumber(1), TokenOperator("+"), TokenNumber(2)]
    run = get_interpreter(tokens)
    assert run is not None
    result = run({})
    assert result == 3

def test_zerodiv_ok():
    tokens = [TokenNumber(1), ManualToken("/", "OPERATOR-INFIX", ""), TokenNumber(0)]
    run = get_interpreter(tokens)
    assert run is not None
    result = run({})
    assert result == "#DIV/0!"

def test_excel_eq_ok():
    tokens = [TokenNumber(1), ManualToken("=", "OPERATOR-INFIX", ""), TokenNumber(0)]
    run = get_interpreter(tokens)
    assert run is not None
    result = run({})
    assert not result

def test_excel_eq_left_error():
    tokens = [TokenError(
        TokenErrorTypes.NUM, "Undefined message"
    ), ManualToken("=", "OPERATOR-INFIX", ""), TokenNumber(0)]
    run = get_interpreter(tokens)
    assert run is not None
    result = run({})
    assert result == "#NUM!"

def test_excel_eq_right_error():
    tokens = [TokenNumber(0),  ManualToken("=", "OPERATOR-INFIX", ""),TokenError(
        TokenErrorTypes.NUM, "Undefined message"
    )]
    run = get_interpreter(tokens)
    assert run is not None
    result = run({})
    assert result == "#NUM!"

def test_excel_op_raise_op_not_implemented():
    tokens = [
        TokenNumber(0),
        ManualToken("%", "OPERATOR-INFIX", "OPEN"),
        TokenNumber(1)
    ]
    f=get_interpreter(tokens)
    assert f is not None
    with pytest.raises(NotImplementedError) as exc_info:
        f({})
    assert str(exc_info.value) == "Operator '%' is not implemented"
