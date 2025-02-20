"""
This module defines various token classes and utility functions for registering and handling operations on tokens.
The valid combinations for the token classes are as follows:
    type: OPERAND
    subtype: LOGICAL | TEXT | NUMBER | ERROR | ARRAY | RANGE

Classes:
    Token: Abstract base class for all tokens.
    BaseToken: Base class implementing the Token interface.
    TokenBool: Token class for boolean values.
    TokenString: Token class for string values.
    TokenNumber: Token class for numeric values.
    TokenFunc: Token class for function names.
    TokenError: Token class for error values.
    TokenErrorTypes: Enum class for different types of token errors.

Functions:
    register_op: Decorator to register operator functions with multiple names.
    register_numeric_op: Decorator to register numeric operator functions with multiple names.

Constants:
    REGISTERED_OPS: Dictionary to store registered operations.
"""

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Dict, Callable, Any, Tuple, Union

__version__ = "0.11.0b1"


class Token(metaclass=ABCMeta):
    """
    Abstract base class for all tokens.
    """

    @property
    @abstractmethod
    def type(self) -> str:
        """Returns the type of the token."""
        pass

    @property
    @abstractmethod
    def subtype(self) -> str:
        """Returns the subtype of the token."""
        pass

    @property
    @abstractmethod
    def value(self) -> Any:
        """Returns the value of the token."""
        pass


class BaseToken(Token):
    """
    Base class implementing the Token interface.
    """

    def __init__(self) -> None:
        super().__init__()
        self._value = None
        self._type = ""
        self._subtype = ""

    @property
    def type(self) -> str:
        """Returns the type of the token."""
        return self._type

    @property
    def subtype(self) -> str:
        """Returns the subtype of the token."""
        return self._subtype

    @property
    def value(self) -> Any:
        """Returns the value of the token."""
        return self._value

    def __repr__(self) -> str:
        """Returns a string representation of the token."""
        return f"Token<v:{self.value} t:{self.type} s:{self.subtype} >"


class TokenBool(BaseToken):
    """
    Token class for boolean values.
    """

    def __init__(self, value: bool) -> None:
        super().__init__()
        self._value = value
        self._type = "OPERAND"
        self._subtype = "LOGICAL"


class TokenString(BaseToken):
    """
    Token class for string values.
    """

    def __init__(self, value: str) -> None:
        super().__init__()
        self._value = value
        self._type = "OPERAND"
        self._subtype = "TEXT"


class TokenNumber(BaseToken):
    """
    Token class for numeric values.
    """

    def __init__(self, value: Union[float, int]) -> None:
        super().__init__()
        self._value = value
        self._type = "OPERAND"
        self._subtype = "NUMBER"


class TokenFunc(BaseToken):
    """
    Token class for function names.
    """

    def __init__(self, func_name: str) -> None:
        super().__init__()
        self._value = func_name
        self._type = "FUNC"
        self._subtype = "OPEN"


class TokenOperator(BaseToken):
    """
    Token class for operators.
    """

    def __init__(self, operator: str) -> None:
        super().__init__()
        self._value = operator
        self._type = "OPERATOR-INFIX"
        self._subtype = ""


class TokenParen(BaseToken):
    """
    Token class for operators.
    """

    def __init__(self, subtype: str) -> None:
        super().__init__()
        self._value = "(" if subtype == "OPEN" else ")"
        self._type = "OPERATOR-INFIX"
        self._subtype = "OPEN" if subtype == "OPEN" else "CLOSE"


class TokenEmpty(BaseToken):
    """
    Token class for empty value.
    """

    def __init__(self) -> None:
        super().__init__()
        self._value = None
        self._type = "OPERAND"
        self._subtype = "EMPTY"


TokenErrorTypes = Enum(
    "TokenErrorTypes",
    [
        ("NULL", "#NULL!"),
        ("ZERO_DIV", "#DIV/0!"),
        ("VALUE", "#VALUE!"),
        ("REF", "#REF!"),
        ("NAME", "#NAME?"),
        ("NUM", "#NUM!"),
        ("NA", "#N/A"),
        ("GETTING_DATA", "#GETTING_DATA"),
    ],
)
"""
Enum class for different types of token errors.
"""


class TokenError(BaseToken):
    """
    Token class for error values.
    """

    def __init__(self, error_type: TokenErrorTypes, message: str) -> None:
        super().__init__()
        self._value = error_type.value
        self._type = "OPERAND"
        self._subtype = "ERROR"
        self._message = message

    @property
    def message(self) -> str:
        """Returns the error message."""
        return self._message


# Dictionary to store registered operations
REGISTERED_OPS: Dict[str, Callable[[Token, Token], Token]] = {}


def register_op(*names):
    """
    Decorator to register operator functions with multiple names.

    Args:
        *names: Variable length argument list of names to register the function under.

    Returns:
        The decorator function.
    """

    def decorator(func: Callable):
        for key in names:
            REGISTERED_OPS[key] = func
        return func  # Ensure the function remains usable normally

    return decorator


OpType = Callable[
    [
        Union[int, float],  # arg: a
        Union[int, float],  # arg: b
    ],
    Union[int, float],  # -> op(a,b)
]

OpRelType = Tuple[str, OpType]


def register_numeric_op(
    *pairs: OpRelType,
):
    """
    Decorator to register numeric operator functions with multiple names.

    Args:
        *pairs: Variable length argument list of tuples containing operator names and functions.

    Returns:
        The decorator function.
    """

    def decorator(
        wrap_operator: Callable[
            [OpType],
            Callable[[Token, Token], Token],
        ],
    ):
        for pair in pairs:
            key, op_func = pair
            REGISTERED_OPS[key] = wrap_operator(op_func)
        return wrap_operator  # Ensure the function remains usable normally

    return decorator
