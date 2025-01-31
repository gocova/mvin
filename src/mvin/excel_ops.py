from mvin import Token, TokenBool, TokenError, TokenErrorTypes, register_op


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
