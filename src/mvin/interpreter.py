from abc import ABCMeta, abstractmethod
from collections import deque
from types import _ReturnT_co
from typing import Any, Callable, Dict, Iterable, Literal, Tuple, List

RPNItemType = Literal["FUNC", "ERROR", "RANGE", "VALUE"]


class Token(metaclass=ABCMeta):
    @property
    @abstractmethod
    def type(self) -> str:
        pass


class RPNItem:
    def __init__(self, type: RPNItemType, value) -> None:
        self.type = type


# Operator precedence and associativity
OPERATORS = {
    "&": (0.5, "L"),  # String concatenation
    "=": (0, "L"),
    "==": (0, "L"),
    "<>": (0, "L"),
    "!=": (0, "L"),
    "<": (0, "L"),
    ">": (0, "L"),
    "<=": (0, "L"),
    ">=": (0, "L"),
    "+": (1, "L"),
    "-": (1, "L"),
    "*": (2, "L"),
    "/": (2, "L"),
    "^": (3, "R"),  # Exponentiation is right-associative
}

DEFAULT_FUNCTIONS = {
    "NOT(": (
        [None],  # Default Argument list
        lambda x: False,
    ),
    "ISERROR(": (
        [None],  # Default Argument list
    ),
    "SEARCH(": (
        [None, None],  # Default Argument list
        lambda a, b: False,
    ),
}


def get_interpreter(
    tokens,  # enumerable
    proposed_functions: Dict[str, Tuple[List | None, Callable]] = DEFAULT_FUNCTIONS,
) -> Callable[[Dict[str, Any], Any]] | None:
    if isinstance(tokens, Iterable):
        functions = {}.update(proposed_functions)
    return None
