import sys

sys.path.append("src")

from mvin import BaseToken, TokenBool, TokenError, TokenErrorTypes, TokenNumber, TokenString
from mvin.functions.excel_lib import excel_search


class ManualToken(BaseToken):
    def __init__(self, value, token_type, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = token_type
        self._subtype = subtype


def test_search_within_text_required():
    result = excel_search(TokenString("a"), None, TokenNumber(1))  # pyright: ignore
    assert isinstance(result, TokenError)
    assert result.value == TokenErrorTypes.VALUE.value


def test_search_within_text_invalid_type():
    result = excel_search(
        TokenString("a"),
        ManualToken("x", "FUNC", "OPEN"),
        TokenNumber(1),
    )
    assert isinstance(result, TokenError)
    assert result.value == TokenErrorTypes.VALUE.value


def test_search_within_text_error_passthrough():
    within_text = TokenError(TokenErrorTypes.REF, "input error")
    result = excel_search(TokenString("a"), within_text, TokenNumber(1))
    assert result is within_text


def test_search_within_text_logical_conversion():
    result = excel_search(TokenString("RU"), TokenBool(True), TokenNumber(1))
    assert isinstance(result, TokenNumber)
    assert result.value == 2


def test_search_find_text_logical_conversion():
    result = excel_search(TokenBool(False), TokenString("XXFALSEYY"), TokenNumber(1))
    assert isinstance(result, TokenNumber)
    assert result.value == 3


def test_search_find_text_error_passthrough():
    find_text = TokenError(TokenErrorTypes.VALUE, "bad find text")
    result = excel_search(find_text, TokenString("abc"), TokenNumber(1))
    assert result is find_text


def test_search_find_text_unsupported_subtype():
    result = excel_search(
        ManualToken("x", "OPERAND", "RANGE"),
        TokenString("abc"),
        TokenNumber(1),
    )
    assert isinstance(result, TokenError)
    assert result.value == TokenErrorTypes.VALUE.value


def test_search_start_num_error_passthrough():
    start_num = TokenError(TokenErrorTypes.VALUE, "bad start")
    result = excel_search(TokenString("a"), TokenString("abc"), start_num)
    assert result is start_num


def test_search_start_num_rejects_non_integer_number():
    result = excel_search(TokenString("a"), TokenString("abc"), TokenNumber(1.5))
    assert isinstance(result, TokenError)
    assert result.value == TokenErrorTypes.VALUE.value
