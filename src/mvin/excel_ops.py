import operator
from mvin import (
    Token,
    TokenBool,
    TokenError,
    TokenErrorTypes,
    TokenNumber,
    TokenString,
    register_numeric_op,
    register_op,
)


@register_op("&")
def excel_op_concat(a: Token, b: Token) -> Token:
    # if a and b: # This part of code cannot be tested
    if a.subtype == "ERROR":
        return a
    if b.subtype == "ERROR":
        return b
    return TokenString(f"{str(a.value)}{str(b.value)}")
    # return TokenError(TokenErrorTypes.NULL) # This part of code cannot be tested


@register_op("=", "==")
def excel_op_eq(a: Token, b: Token) -> Token:
    if a and b and a.type == "OPERAND" and b.type == "OPERAND":
        return TokenBool(a.subtype == b.subtype and a.value == b.value)
    else:
        if a and a.subtype == "ERROR":
            return a
        elif b and b.subtype == "ERROR":
            return b
        return TokenError(
            TokenErrorTypes.REF,
            "Expected 2 values but, at most, 1 argument was a value",
        )


@register_op("<>", "!=")
def excel_op_neq(a: Token, b: Token) -> Token:
    possible_eq = excel_op_eq(a, b)
    if possible_eq and possible_eq.subtype == "LOGICAL":
        return TokenBool(not possible_eq.value)
    return possible_eq


@register_numeric_op(
    ("<", operator.lt),
    (">", operator.gt),
    ("<=", operator.le),
    (">=", operator.ge),
    ("+", operator.add),
    ("-", operator.sub),
    ("*", operator.mul),
    ("/", operator.truediv),
    ("^", operator.pow),
)
def wrap_excel_numeric_op(operator_func):
    def excel_numeric_op(a: Token, b: Token) -> Token:
        # print(f"a -> {a}")
        # print(f"b -> {b}")
        if a and b:
            if a.subtype == "ERROR":
                return a
            if b.subtype == "ERROR":
                return b
            if (a.subtype == "NUMBER" and b.subtype == "NUMBER") and (
                a.type == "OPERAND" and b.type == "OPERAND"
            ):
                return TokenNumber(operator_func(a.value, b.value))
        return TokenError(
            TokenErrorTypes.NUM,
            "Both arguments are not defined"
            if a is None and b is None
            else (
                "The first argument is not defined"
                if a is None
                else "The second argument is not defined"
            ),
        )

    return excel_numeric_op
