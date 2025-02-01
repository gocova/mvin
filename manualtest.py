import sys

sys.path.append("src")

from mvin import BaseToken, TokenString, TokenNumber
from mvin.interpreter import get_interpreter

import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class ManualToken(BaseToken):
    def __init__(self, value, type, subtype) -> None:
        super().__init__()
        self._value = value
        self._type = type
        self._subtype = subtype


tokens = [
    TokenString("hi "),
    TokenString("world"),
    ManualToken("&", "OPERATOR-INFIX", ""),
]
run = get_interpreter(tokens)
if run:
    print(run({}))

tokens = [TokenNumber(1), TokenNumber(2), ManualToken("+", "OPERATOR-INFIX", "")]
run = get_interpreter(tokens)
if run:
    print(run({}))
