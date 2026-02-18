# import pytest # required for pytest.raises

from mvin import BaseToken, TokenError, TokenErrorTypes, TokenNumber, TokenString
from mvin.functions.excel_lib import excel_not
from mvin.interpreter import get_interpreter


class ManualToken(BaseToken):
    def __init__(self, value, type, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = type
        self._subtype = subtype


class FalseyToken(BaseToken):
    def __init__(self, value, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = "OPERAND"
        self._subtype = subtype

    def __bool__(self):
        return False


def test_excel_not_numeric_arg():
    tokens = [
        ManualToken("NOT(", "FUNC", "OPEN"),
        TokenNumber(1),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert not f({})

def test_excel_not_direct_none():
    res = excel_not(None) # pyright: ignore
    assert res is not None
    assert res != TokenErrorTypes.VALUE.value

def test_excel_iserror_false():
    tokens = [
        ManualToken("ISERROR(", "FUNC", "OPEN"),
        TokenNumber(1),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert not f({})

def test_excel_iserror_false_with_string():
    tokens = [
        ManualToken("ISERROR(", "FUNC", "OPEN"),
        TokenString("hi"),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert not f({})

def test_excel_iserror_true():
    tokens = [
        ManualToken("ISERROR(", "FUNC", "OPEN"),
        TokenError(
            TokenErrorTypes.VALUE
            , "Defined error"
        ),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    f = get_interpreter(tokens)
    assert f is not None
    assert f({})


def test_excel_not_accepts_falsey_numeric_token():
    result = excel_not(FalseyToken(0, "NUMBER"))
    assert result.value
