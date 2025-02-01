import sys
sys.path.append('src')

from mvin import BaseToken, TokenBool, TokenError, TokenErrorTypes, TokenNumber, TokenString
from mvin.interpreter import get_interpreter

def test_basetoken():
    base = BaseToken()

class ManualToken(BaseToken):
    def __init__(self, value, type, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = type
        self._subtype = subtype

def test_concat_ok():
    tokens = [TokenString("hi "), TokenString("world"), ManualToken("&", "OPERATOR-INFIX", "")]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == "hi world"

def test_concat_left_err():
    tokens = [TokenError(
        TokenErrorTypes.REF, "Undefined message"
    ), TokenString("world"), ManualToken("&", "OPERATOR-INFIX", "")]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == "#REF!"

def test_concat_right_err():
    tokens = [TokenString("hi "), TokenError(
        TokenErrorTypes.REF, "Undefined message"
    ), ManualToken("&", "OPERATOR-INFIX", "")]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == "#REF!"

def test_concat_numeric_ok():
    tokens = [TokenNumber(1), TokenNumber(2), ManualToken("&", "OPERATOR-INFIX", "")]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == "12"

def test_add_ok():
    tokens = [TokenNumber(1), TokenNumber(2), ManualToken("+", "OPERATOR-INFIX", "")]
    run = get_interpreter(tokens)
    assert run is not None
    result = run({})
    assert result == 3

def test_zerodiv_ok():
    tokens = [TokenNumber(1), TokenNumber(0), ManualToken("/", "OPERATOR-INFIX", "")]
    run = get_interpreter(tokens)
    assert run is not None
    result = run({})
    assert result == "#DIV/0!"
