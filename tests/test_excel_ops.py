import sys

sys.path.append("src")

from mvin import BaseToken, TokenNumber, TokenString
import mvin.excel_ops as e_ops
from operator import add


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


def test_concat_ret_error():
    num_token = TokenNumber(2)
    assert e_ops.excel_op_concat(None, num_token).value == "#REF!"
    assert e_ops.excel_op_concat(num_token, None).value == "#REF!"


def test_eq_ret_error():
    text_token = TokenString("hi")
    assert e_ops.excel_op_eq(None, text_token).value == "#VALUE!"
    assert e_ops.excel_op_eq(text_token, None).value == "#VALUE!"


def test_neq_ok():
    text_token_a = TokenString("hi")
    text_token_b = TokenString("hi")
    assert not e_ops.excel_op_neq(text_token_a, text_token_b).value
    text_token_c = TokenString("world")
    assert e_ops.excel_op_neq(text_token_a, text_token_c).value


def test_neq_ret_error():
    text_token_a = TokenString("hi")
    assert e_ops.excel_op_neq(text_token_a, None).value == "#VALUE!"


def test_numeric_op_wrapper_ok():
    add_op = e_ops.wrap_excel_numeric_op(add)
    num_token = TokenNumber(2)
    assert add_op(num_token, num_token).value == 4


def test_numeric_op_wrapper_none_arg():
    add_op = e_ops.wrap_excel_numeric_op(add)
    num_token = TokenNumber(2)
    assert add_op(num_token, None).value == "#NUM!"  # pyright: ignore


def test_numeric_op_wrapper_error_arg():
    add_op = e_ops.wrap_excel_numeric_op(add)
    num_token = TokenNumber(2)
    error_token = ManualToken("#VALUE!", "OPERAND", "ERROR")
    assert add_op(num_token, error_token).value == "#VALUE!"  # pyright: ignore
    assert add_op(error_token, num_token).value == "#VALUE!"  # pyright: ignore


def test_numeric_op_wrapper_num_and_string():
    add_op = e_ops.wrap_excel_numeric_op(add)
    num_token = TokenNumber(2)
    text_token = TokenString("hi")
    assert add_op(num_token, text_token).value == "#NUM!"


def test_concat_accepts_falsey_custom_tokens():
    left = FalseyToken(0, "NUMBER")
    right = FalseyToken(1, "NUMBER")
    assert e_ops.excel_op_concat(left, right).value == "01"


def test_eq_accepts_falsey_custom_tokens():
    left = FalseyToken(0, "NUMBER")
    right = FalseyToken(0, "NUMBER")
    assert e_ops.excel_op_eq(left, right).value
