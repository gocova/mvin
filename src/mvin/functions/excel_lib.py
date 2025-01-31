from typing import Callable, Dict, List, Tuple
from mvin import Token, TokenBool, TokenError, TokenErrorTypes


def excel_not(token: Token) -> Token:
    if token and token.type == "OPERAND":
        if token.subtype == "LOGICAL":
            return TokenBool(not token.value)
        elif token.subtype == "NUMBER":
            return TokenBool(not (token.value != 0))
    return TokenError(
        TokenErrorTypes.VALUE,
        f"Expected boolean or number but '{token.subtype}' was found (value: {token.value}",
    )


def excel_iserror(token: Token) -> Token:
    return TokenBool(token and token.subtype == "ERROR")


DEFAULT_FUNCTIONS: Dict[str, Tuple[List | None, Callable]] = {
    "NOT(": (
        [
            None
        ],  # default argument list (if None is in the list, that argument is not optional)
        excel_not,
    ),
    "ISERROR(": (
        [
            None
        ],  # default argument list (if None is in the list, that argument is not optional)
        excel_iserror,
    ),
}
