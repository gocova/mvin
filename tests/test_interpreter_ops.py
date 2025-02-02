import sys

import pytest
sys.path.append('src')

from mvin import BaseToken, TokenError, TokenErrorTypes, TokenNumber, TokenString
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
    tokens = [TokenNumber(1), ManualToken("+", "OPERATOR-INFIX", ""), TokenNumber(2)]
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
    assert result == False

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

# def test_excel_eq_non_value():
#     tokens = [TokenNumber(0),TokenError(
#         TokenErrorTypes.NUM, "Undefined message"
#     ),  ManualToken("NOT(", "FUNC", "OPEN")]
#     run = get_interpreter(tokens)
#     assert run is not None
#     result = run({})
#     assert result == "#NUM!"
