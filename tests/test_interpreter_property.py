from hypothesis import given, settings
from hypothesis import strategies as st

from mvin import BaseToken, TokenNumber
from mvin.interpreter import get_interpreter


class ManualToken(BaseToken):
    def __init__(self, value, token_type, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = token_type
        self._subtype = subtype


@settings(max_examples=75, deadline=None)
@given(
    a=st.integers(min_value=-10_000, max_value=10_000),
    b=st.integers(min_value=-10_000, max_value=10_000),
    c=st.integers(min_value=-10_000, max_value=10_000),
)
def test_property_operator_precedence_matches_python_for_add_mul(a, b, c):
    tokens = [
        TokenNumber(a),
        ManualToken("+", "OPERATOR-INFIX", ""),
        TokenNumber(b),
        ManualToken("*", "OPERATOR-INFIX", ""),
        TokenNumber(c),
    ]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == a + b * c


@settings(max_examples=75, deadline=None)
@given(value=st.integers(min_value=-10_000, max_value=10_000))
def test_property_unary_minus_matches_python(value):
    tokens = [ManualToken("-", "OPERATOR-PREFIX", ""), TokenNumber(value)]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == -value


@settings(max_examples=75, deadline=None)
@given(
    left=st.integers(min_value=-10_000, max_value=10_000),
    right=st.integers(min_value=-10_000, max_value=10_000),
)
def test_property_unary_minus_after_infix(left, right):
    tokens = [
        TokenNumber(left),
        ManualToken("+", "OPERATOR-INFIX", ""),
        ManualToken("-", "OPERATOR-PREFIX", ""),
        TokenNumber(right),
    ]
    run = get_interpreter(tokens)
    assert run is not None
    assert run({}) == left + (-right)
