from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Dict, Callable, Any


class Token(metaclass=ABCMeta):
    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @property
    @abstractmethod
    def subtype(self) -> str:
        pass

    @property
    @abstractmethod
    def value(self) -> Any:
        pass


class BaseToken(Token):
    def __init__(self) -> None:
        super().__init__()
        self._value = None
        self._type = ""
        self._subtype = ""

    @property
    def type(self) -> str:
        return self._type

    @property
    def subtype(self) -> str:
        return self._subtype

    @property
    def value(self) -> Any:
        return self._value


class TokenBool(BaseToken):
    def __init__(self, value: bool) -> None:
        super().__init__()
        self._value = value
        self._type = "OPERAND"
        self._subtype = "LOGICAL"


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


class TokenError(BaseToken):
    def __init__(self, error_type: TokenErrorTypes, message: str) -> None:
        super().__init__()
        self._value = error_type.value
        self._type = "OPERAND"
        self._subtype = "ERROR"
        self._message = message

    @property
    def message(self) -> str:
        return self._message


# Dictionary to store registered operations
REGISTERED_OPS: Dict[str, Callable[[Token, Token], Token]] = {}


# Decorator to register operator functions with multiple names
def register_op(*names):
    def decorator(func: Callable):
        for key in names:
            REGISTERED_OPS[key] = func
        return func  # Ensure the function remains usable normally

    return decorator
