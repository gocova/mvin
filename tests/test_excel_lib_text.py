import sys

sys.path.append("src")

from mvin import BaseToken, TokenBool, TokenError, TokenErrorTypes, TokenNumber, TokenString
from mvin.functions.excel_lib import excel_left, excel_len, excel_right


class ManualToken(BaseToken):
    def __init__(self, value, token_type, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = token_type
        self._subtype = subtype


def test_left_basic_and_type_conversions():
    assert excel_left(TokenString("hello"), TokenNumber(2)).value == "he"
    assert excel_left(TokenNumber(12345), TokenNumber(3)).value == "123"
    assert excel_left(TokenBool(True), TokenNumber(4)).value == "TRUE"


def test_left_default_num_chars():
    result = excel_left(TokenString("hello"), None)
    assert isinstance(result, TokenString)
    assert result.value == "h"


def test_left_invalid_input_paths():
    assert excel_left(None, TokenNumber(1)).value == TokenErrorTypes.VALUE.value  # pyright: ignore
    assert (
        excel_left(ManualToken("x", "FUNC", "OPEN"), TokenNumber(1)).value
        == TokenErrorTypes.VALUE.value
    )
    assert (
        excel_left(TokenString("hello"), ManualToken("x", "FUNC", "OPEN")).value
        == TokenErrorTypes.VALUE.value
    )
    assert (
        excel_left(TokenString("hello"), TokenString("2")).value
        == TokenErrorTypes.VALUE.value
    )
    assert (
        excel_left(TokenString("hello"), TokenNumber(-1)).value
        == TokenErrorTypes.VALUE.value
    )
    assert (
        excel_left(TokenString("hello"), TokenNumber(1.5)).value
        == TokenErrorTypes.VALUE.value
    )


def test_left_error_passthroughs():
    text_error = TokenError(TokenErrorTypes.REF, "bad text")
    chars_error = TokenError(TokenErrorTypes.VALUE, "bad chars")
    assert excel_left(text_error, TokenNumber(1)) is text_error
    assert excel_left(TokenString("hello"), chars_error) is chars_error


def test_left_unsupported_text_subtype():
    result = excel_left(ManualToken("x", "OPERAND", "RANGE"), TokenNumber(1))
    assert isinstance(result, TokenError)
    assert result.value == TokenErrorTypes.VALUE.value


def test_right_basic_and_type_conversions():
    assert excel_right(TokenString("hello"), TokenNumber(2)).value == "lo"
    assert excel_right(TokenNumber(12345), TokenNumber(3)).value == "345"
    assert excel_right(TokenBool(False), TokenNumber(5)).value == "FALSE"


def test_right_default_num_chars():
    result = excel_right(TokenString("hello"), None)
    assert isinstance(result, TokenString)
    assert result.value == "o"


def test_right_invalid_input_paths():
    assert excel_right(None, TokenNumber(1)).value == TokenErrorTypes.VALUE.value  # pyright: ignore
    assert (
        excel_right(ManualToken("x", "FUNC", "OPEN"), TokenNumber(1)).value
        == TokenErrorTypes.VALUE.value
    )
    assert (
        excel_right(TokenString("hello"), ManualToken("x", "FUNC", "OPEN")).value
        == TokenErrorTypes.VALUE.value
    )
    assert (
        excel_right(TokenString("hello"), TokenString("2")).value
        == TokenErrorTypes.VALUE.value
    )
    assert (
        excel_right(TokenString("hello"), TokenNumber(-1)).value
        == TokenErrorTypes.VALUE.value
    )
    assert (
        excel_right(TokenString("hello"), TokenNumber(1.5)).value
        == TokenErrorTypes.VALUE.value
    )


def test_right_zero_num_chars_returns_empty_string():
    result = excel_right(TokenString("hello"), TokenNumber(0))
    assert isinstance(result, TokenString)
    assert result.value == ""


def test_right_error_passthroughs():
    text_error = TokenError(TokenErrorTypes.REF, "bad text")
    chars_error = TokenError(TokenErrorTypes.VALUE, "bad chars")
    assert excel_right(text_error, TokenNumber(1)) is text_error
    assert excel_right(TokenString("hello"), chars_error) is chars_error


def test_right_unsupported_text_subtype():
    result = excel_right(ManualToken("x", "OPERAND", "RANGE"), TokenNumber(1))
    assert isinstance(result, TokenError)
    assert result.value == TokenErrorTypes.VALUE.value


def test_len_basic_and_type_conversions():
    assert excel_len(TokenString("hello")).value == 5
    assert excel_len(TokenNumber(12345)).value == 5
    assert excel_len(TokenBool(True)).value == 4


def test_len_invalid_input_paths():
    assert excel_len(None).value == TokenErrorTypes.VALUE.value  # pyright: ignore
    assert excel_len(ManualToken("x", "FUNC", "OPEN")).value == TokenErrorTypes.VALUE.value
    assert excel_len(ManualToken("x", "OPERAND", "RANGE")).value == TokenErrorTypes.VALUE.value


def test_len_error_passthrough():
    text_error = TokenError(TokenErrorTypes.REF, "bad text")
    assert excel_len(text_error) is text_error
