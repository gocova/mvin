import sys
sys.path.append('src')

# import pytest # required for pytest.raises

from mvin.functions.excel_lib import excel_search
from mvin import TokenString, TokenNumber, TokenError, TokenErrorTypes

def test_excel_search_found():
    find_text = TokenString("world")
    within_text = TokenString("hello world")
    start_num = TokenNumber(1)
    result = excel_search(find_text, within_text, start_num)
    assert isinstance(result, TokenNumber)
    assert result.value == 7

def test_excel_search_not_found():
    find_text = TokenString("world")
    within_text = TokenString("hello")
    start_num = TokenNumber(1)
    result = excel_search(find_text, within_text, start_num)
    assert isinstance(result, TokenError)
    assert result.value == TokenErrorTypes.VALUE.value

def test_excel_search_with_start_num():
    find_text = TokenString("world")
    within_text = TokenString("hello world world")
    start_num = TokenNumber(8)
    result = excel_search(find_text, within_text, start_num)
    assert isinstance(result, TokenNumber)
    assert result.value == 13

def test_excel_search_with_negative_start_num():
    find_text = TokenString("world")
    within_text = TokenString("hello world world")
    start_num = TokenNumber(-8)
    result = excel_search(find_text, within_text, start_num)
    assert isinstance(result, TokenError)
    assert result.value == TokenErrorTypes.VALUE.value
    assert result.message == "Expected integer >= 1 for start_num argument, but found: -8"


def test_excel_search_invalid_start_num():
    find_text = TokenString("world")
    within_text = TokenString("hello world")
    start_num = TokenString("invalid")
    result = excel_search(find_text, within_text, start_num)
    assert isinstance(result, TokenError)
    assert result.value == TokenErrorTypes.VALUE.value

def test_excel_search_error_in_start_num():
    find_text = TokenString("world")
    within_text = TokenString("hello world")
    start_num = TokenError(TokenErrorTypes.VALUE, "Error")
    result = excel_search(find_text, within_text, start_num)
    assert isinstance(result, TokenError)
    assert result.value == TokenErrorTypes.VALUE.value
