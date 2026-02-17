import sys

sys.path.append("src")

from mvin import TokenEmpty, TokenParen


def test_token_paren_and_empty():
    open_paren = TokenParen("OPEN")
    close_paren = TokenParen("CLOSE")
    empty = TokenEmpty()

    assert open_paren.value == "("
    assert open_paren.type == "OPERATOR-INFIX"
    assert open_paren.subtype == "OPEN"

    assert close_paren.value == ")"
    assert close_paren.type == "OPERATOR-INFIX"
    assert close_paren.subtype == "CLOSE"

    assert empty.value is None
    assert empty.type == "OPERAND"
    assert empty.subtype == "EMPTY"
