import logging
from typing import Callable, Dict, List, Tuple, Union
from mvin import Token, TokenBool, TokenError, TokenErrorTypes, TokenNumber, TokenString


def excel_not(token: Token) -> Token:
    if token and token.type == "OPERAND":
        if token.subtype == "LOGICAL":
            return TokenBool(not token.value)
        elif token.subtype == "NUMBER":
            return TokenBool(not (token.value != 0))
    return TokenError(
        TokenErrorTypes.VALUE,
        f"Expected boolean or number and found {token}",
    )


def excel_iserror(token: Token) -> Token:
    return TokenBool(token and token.subtype == "ERROR")


def excel_search(
    find_text: Union[Token, None],
    within_text: Union[Token, None],
    start_num: Union[Token, None],
) -> Token:
    logging.debug(
        f"excel_lib.excel_search: calling with (find_text= {find_text}, within_text={within_text}, start_num= {start_num} )"
    )
    if not within_text:
        return TokenError(TokenErrorTypes.VALUE, "Argument within_text cannot be None")
    if within_text.type != "OPERAND":
        return TokenError(
            TokenErrorTypes.VALUE,
            f"Expected value for within_text argument, but found: {within_text}",
        )

    within_text_value = ""
    if within_text:
        if within_text.subtype == "ERROR":
            return within_text
        elif within_text.subtype == "TEXT":
            within_text_value = within_text.value
        elif within_text.subtype == "NUMBER":
            within_text_value = str(within_text.value)
        elif within_text.subtype == "LOGICAL":
            within_text_value = "TRUE" if within_text.value else "FALSE"
        else:
            return TokenError(
                TokenErrorTypes.VALUE,
                f"Unsupported value type for within_text argument: {within_text}",
            )

    find_text_value = ""
    if find_text:
        if find_text.subtype == "ERROR":
            return find_text
        elif find_text.subtype == "TEXT":
            find_text_value = find_text.value
        elif find_text.subtype == "NUMBER":
            find_text_value = str(find_text.value)
        elif find_text.subtype == "LOGICAL":
            find_text_value = "TRUE" if find_text.value else "FALSE"
        else:
            return TokenError(
                TokenErrorTypes.VALUE,
                f"Unsupported value type for find_text argument: {find_text}",
            )

    start_num_value = 0
    if start_num:
        if start_num.subtype == "ERROR":
            return start_num
        elif start_num.subtype == "NUMBER":
            start_num_value = start_num.value - 1

            if start_num_value < 0:
                return TokenError(
                    TokenErrorTypes.VALUE,
                    f"Expected integer >=1 for start_num argument, but found: {start_num.value}",
                )
        else:
            return TokenError(
                TokenErrorTypes.VALUE,
                f"Expected integer value for start_num argument, but found: {start_num}",
            )

    found_index = within_text_value.find(find_text_value, start_num_value)
    if found_index >= 0:
        return TokenNumber(found_index + 1)
    else:
        return TokenError(
            TokenErrorTypes.VALUE,
            f"Text `{find_text_value}` not found in text `{within_text_value} (starting at: {start_num_value + 1})`",
        )


def excel_left(text: Union[Token, None], num_chars: Union[Token, None]) -> Token:
    logging.debug(
        f"excel_lib.excel_left: calling with (text= {text}, num_chars= {num_chars} )"
    )
    if not text:
        return TokenError(
            TokenErrorTypes.VALUE,
            "Expected value for text argument, but Empty was found",
        )
    if text.type != "OPERAND":
        return TokenError(
            TokenErrorTypes.VALUE,
            f"Expected value for text argument, but found: {text}",
        )

    if num_chars and num_chars.type != "OPERAND":
        return TokenError(
            TokenErrorTypes.VALUE,
            f"Expected positive integer for num_chars argument, but found: {num_chars}",
        )

    text_value = ""
    if text.subtype == "ERROR":
        return text
    elif text.subtype == "TEXT":
        text_value = text.value
    elif text.subtype == "NUMBER":
        text_value = str(text.value)
    elif text.subtype == "LOGICAL":
        text_value = "TRUE" if text.value else "FALSE"
    else:
        return TokenError(
            TokenErrorTypes.VALUE,
            f"Unsupported value type for text argument: {text}",
        )

    num_chars_value = 1
    if num_chars:
        if num_chars.subtype == "ERROR":
            return num_chars
        elif num_chars.subtype == "NUMBER":
            num_chars_value = num_chars.value

            if num_chars_value < 0:
                return TokenError(
                    TokenErrorTypes.VALUE,
                    f"Expected positive integer for num_chars argument, but found: {num_chars.value}",
                )
        else:
            return TokenError(
                TokenErrorTypes.VALUE,
                f"Expected positive integer for num_chars argument, but found: {num_chars}",
            )

    return TokenString(text_value[0:num_chars_value])


DEFAULT_FUNCTIONS: Dict[str, Tuple[Union[List, None], Callable]] = {
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
    "SEARCH(": (
        [
            TokenString(""),  # find_text
            None,  # within_text
            TokenNumber(1),  # start_num <- default: 1
        ],  # default argument list (if None is in the list, that argument is not optional)
        excel_search,
    ),
    "LEFT(": (
        [
            None,  # text <- required
            TokenNumber(1),  # num_chars <- Optional, default: 1
        ],  # default argument list (if None is in the list, that argument is not optional)
        excel_left,
    ),
}
