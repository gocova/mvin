import sys

sys.path.append("src")

import pytest  # required for pytest.raises

from mvin import BaseToken, Token, TokenBool, TokenError, TokenErrorTypes, TokenNumber, TokenOperator, TokenString
from mvin.interpreter import get_interpreter


class ManualToken(BaseToken):
    def __init__(self, value, token_type, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = token_type
        self._subtype = subtype


class FalseyToken(BaseToken):
    def __init__(self, value, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = "OPERAND"
        self._subtype = subtype

    def __bool__(self):
        return False


def test_abstractToken():
    with pytest.raises(TypeError):
        _ = Token()  # pyright: ignore


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


def test_range_missing_args():
    tokens = [ManualToken("F7", "OPERAND", "RANGE")]
    run = get_interpreter(tokens)
    assert run is not None
    with pytest.raises(KeyError):
        _ = run({})


def test_range_proper_value_transfer():
    tokens = [ManualToken("F7", "OPERAND", "RANGE")]
    run = get_interpreter(tokens)
    assert run is not None
    result = run({"F7": TokenString("done")})
    assert result == "done"


def test_range_falsey_input_token_is_accepted():
    tokens = [ManualToken("F7", "OPERAND", "RANGE")]
    run = get_interpreter(tokens)
    assert run is not None
    result = run({"F7": FalseyToken(0, "NUMBER")})
    assert result == 0


def test_registered_ops_are_copied_defensively():
    def add_v1(a, b):
        return TokenNumber(10)

    def add_v2(a, b):
        return TokenNumber(99)

    custom_ops = {"+": add_v1}
    run = get_interpreter(
        [TokenNumber(1), TokenOperator("+"), TokenNumber(2)],
        registered_ops=custom_ops,
    )
    assert run is not None

    custom_ops["+"] = add_v2
    assert run({}) == 10


def test_function_map_is_copied_defensively():
    def f_v1(value):
        return TokenNumber(value.value + 1)

    def f_v2(value):
        return TokenNumber(value.value + 100)

    custom_functions = {"INC(": ([None], f_v1)}
    tokens = [
        ManualToken("INC(", "FUNC", "OPEN"),
        TokenNumber(1),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    run = get_interpreter(tokens, proposed_functions=custom_functions)
    assert run is not None

    custom_functions["INC("] = ([None], f_v2)
    assert run({}) == 2


def test_function_can_return_falsey_token():
    def f_falsey(value):
        return FalseyToken(value.value - 1, "NUMBER")

    custom_functions = {"DEC(": ([None], f_falsey)}
    tokens = [
        ManualToken("DEC(", "FUNC", "OPEN"),
        TokenNumber(1),
        ManualToken(")", "FUNC", "CLOSE"),
    ]
    run = get_interpreter(tokens, proposed_functions=custom_functions)
    assert run is not None
    assert run({}) == 0


def test_none_as_token():
    tokens = [None]
    with pytest.raises(SyntaxError):
        get_interpreter(tokens)  # pyright: ignore


def test_none_as_list():
    run_as_none = get_interpreter(None)  # pyright: ignore
    assert run_as_none is None
