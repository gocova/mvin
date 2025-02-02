from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Dict, Callable, Any, Tuple


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

    def __repr__(self) -> str:
        return f"Token<v:{self.value} t:{self.type} s:{self.subtype} >"


class TokenBool(BaseToken):
    def __init__(self, value: bool) -> None:
        super().__init__()
        self._value = value
        self._type = "OPERAND"
        self._subtype = "LOGICAL"


class TokenString(BaseToken):
    def __init__(self, value: str) -> None:
        super().__init__()
        self._value = value
        self._type = "OPERAND"
        self._subtype = "TEXT"


class TokenNumber(BaseToken):
    def __init__(self, value: float | int) -> None:
        super().__init__()
        self._value = value
        self._type = "OPERAND"
        self._subtype = "NUMBER"


class TokenFunc(BaseToken):
    def __init__(self, func_name: str) -> None:
        super().__init__()
        self._value = func_name
        self._type = "FUNC"
        self._subtype = "OPEN"


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


OpType = Callable[  # operator
    [  # operator arguments
        int | float,  # arg: a
        int | float,  # arg: b
    ],  # returning
    int | float,  # -> op(a,b)
]

OpRelType = Tuple[str, OpType]


def register_numeric_op(
    *pairs: OpRelType,  # by using * we are stating that we will have a variable number of OpRelType (like Tuple[OpRelType,...])
):
    def decorator(
        wrap_operator: Callable[
            [  # arguments
                OpType
            ],  # returns
            Callable[[Token, Token], Token],
        ],
    ):
        for pair in pairs:
            key, op_func = pair
            REGISTERED_OPS[key] = wrap_operator(op_func)
        return wrap_operator  # Ensure the function remains usable normally

    return decorator
