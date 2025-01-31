import logging
import typing
from collections import deque
from types import MappingProxyType
from typing import Any, Callable, Dict, List, Mapping, Sequence, Set, Tuple

from mvin import REGISTERED_OPS, Token, TokenError, TokenErrorTypes
from mvin.functions.excel_lib import DEFAULT_FUNCTIONS

# Operator precedence and associativity
OPERATORS: Mapping[str, Tuple[int | float, str]] = MappingProxyType(
    {
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
)


def get_interpreter(
    tokens: Sequence[Token],  # enumerable
    registered_ops: Dict[str, Callable[[Token, Token], Token]] = REGISTERED_OPS,
    proposed_functions: Dict[str, Tuple[List | None, Callable]] = DEFAULT_FUNCTIONS,
) -> Callable[[Dict[str, Any], Any]] | None:
    if isinstance(tokens, Sequence):
        ops = MappingProxyType(registered_ops)
        functions = MappingProxyType(proposed_functions)

        def infix_to_rpn(
            tokens: Sequence[Token],  # tokens from the tokenizer
            functions: Mapping[str, Tuple[List | None, Callable]],
        ) -> Tuple[Tuple[Token], Set[str]]:
            """
            Convert an infix expression to Reverse Polish Notation (RPN).

                Args:
                    tokens (list): A list of tokens representing the infix expression.

                Returns:
                    list: A list of tokens in Reverse Polish Notation (RPN).

                Raises:
                    SyntaxError: If there are syntax errors in the infix expression.

                The function processes the input tokens and converts them to RPN format.
                It handles operators, operands, parentheses, and functions, ensuring proper
                syntax and operator precedence. The function uses two stacks to manage
                operators and argument counts, and includes detailed error handling to
                provide informative messages for various syntax issues.
            """
            output = []
            op_stack = deque()
            arg_stack = (
                deque()
            )  # Keeps track of argument counts for nested function calls
            open_parens = 0

            inputs: Set[str] = set()

            for i, token in enumerate(tokens):
                logging.debug(
                    f"--------\noutput: {output}\nop_stack: {op_stack}\narg_count: {arg_stack}\ntoken: {token}"
                )
                if token.type == "OPERAND":
                    output.append(token)

                    if token.subtype == "RANGE":
                        inputs.add(token.value)

                elif token.type == "FUNC" and token.subtype == "OPEN":
                    func_name = token.value
                    if func_name not in functions:
                        raise SyntaxError(
                            f"Unsupported function `{token.value}` at position {i}."
                        )
                    op_stack.append(func_name)
                    arg_stack.append(
                        1
                    )  # Start with one argument for this instance of the function

                    op_stack.append("(")
                    open_parens += 1

                elif token.type == "OPERATOR-INFIX":
                    if i == 0 or (
                        tokens[i - 1].type == "OPERATOR-INFIX"
                        or tokens[i - 1].value == "("
                    ):
                        raise SyntaxError(
                            f"Unexpected operator `{token}` at position {i}."
                        )
                    token_value = token.value
                    while (
                        op_stack
                        and op_stack[-1] in OPERATORS
                        and (
                            (
                                OPERATORS[token_value][1] == "L"
                                and OPERATORS[token_value][0]
                                <= OPERATORS[op_stack[-1]][0]
                            )
                            or (
                                OPERATORS[token_value][1] == "R"
                                and OPERATORS[token_value][0]
                                < OPERATORS[op_stack[-1]][0]
                            )
                        )
                    ):
                        output.append(op_stack.pop())
                    op_stack.append(token_value)

                elif token.value == "(":  # Left parenthesis
                    if i > 0 and tokens[i - 1].type == "OPERAND":
                        raise SyntaxError(
                            f"Missing operator before '(' at position {i}."
                        )
                    op_stack.append(token.value)
                    open_parens += 1

                elif token.value == ")":  # Right parenthesis
                    open_parens -= 1
                    if open_parens < 0:
                        raise SyntaxError(
                            f"Unexpected `)` at position {i} (too many closing parentheses)."
                        )

                    # Ensure trailing empty argument handling
                    last_token = tokens[i - 1] if i > 0 else None
                    logging.debug(f"last_token: {last_token}")
                    if token.type == "FUNC" and token.subtype == "OPEN":
                        func_name = token.value
                        if (
                            functions[func_name] == ()
                        ):  # Zero-arg function, no need for 'None'
                            arg_stack[-1] = 0
                        else:
                            output.append("None")  # Mark missing argument

                    elif last_token and last_token.value == ",":
                        output.append("None")  # Handle missing last argument

                    while op_stack and op_stack[-1] != "(":
                        output.append(op_stack.pop())

                    if not op_stack:
                        raise SyntaxError(f"Unmatched `)` at position {i}.")
                    op_stack.pop()  # Remove '('

                    if op_stack and token.type == "FUNC" and token.subtype == "CLOSE":
                        func_name = op_stack.pop()
                        arg_count = arg_stack.pop()  # Use dynamic argument count
                        defined_func_args = functions[func_name]
                        if (
                            defined_func_args is not None
                            and len(defined_func_args) != arg_count
                        ):
                            raise SyntaxError(
                                f"Function `{func_name}` expects {len(defined_func_args)} arguments but got {arg_count}."
                            )
                        output.append(func_name)
                        output.append(arg_count)

                elif (
                    token.type == "SEP" and token.subtype == "ARG"
                ):  # token.value == ',':
                    if tokens[i - 1].subtype == "OPEN" or tokens[i - 1].value == ",":
                        output.append(None)  # Handle missing argument

                    while op_stack and op_stack[-1] != "(":
                        output.append(op_stack.pop())

                    if arg_stack:
                        arg_stack[-1] += (
                            1  # Increase count for the current function call
                        )

                elif token.type == "WHITE-SPACE":
                    pass

                else:
                    raise SyntaxError(f"Unrecognized token `{token}` at position {i}.")

            if open_parens > 0:
                raise SyntaxError("Unmatched `(` (missing closing parenthesis).")

            while op_stack:
                if op_stack[-1] == "(":
                    raise SyntaxError("Unmatched `(` in expression.")
                output.append(op_stack.pop())

            return tuple(output), inputs

        rpn_tokens, inputs = infix_to_rpn(tokens, functions)

        def execute_func(
            rpn_tokens: Tuple[Token], inputs_set: Set[str]
        ) -> Callable[[Dict[str, typing.Any]], Any]:
            def evaluate_rpn(inputs: Dict[str, typing.Any] = {}) -> typing.Any:
                immutable_inputs: Mapping[str, Any] = MappingProxyType(inputs)

                stack = deque()

                for token in rpn_tokens:
                    if token.type == "OPERAND":
                        if token.subtype != "RANGE":
                            stack.append(token)
                        else:
                            range_value = immutable_inputs.get(token.value)
                            if range_value:
                                stack.append(range_value)
                            else:
                                raise KeyError(
                                    f"The input '{token.value}' is required but was not found in the provided inputs."
                                )
                    elif token.type == "OPERATOR-INFIX":  # in OPERATORS:
                        if len(stack) < 2:
                            raise ValueError(
                                f"Not enough values for operation '{token.value}'."
                            )
                        b = stack.pop()
                        a = stack.pop()

                        if (
                            token.value == "/"
                            and b.type == "OPERAND"
                            and (b.value == 0 or b.value == 0.0)
                        ):
                            stack.append(
                                TokenError(
                                    TokenErrorTypes.ZERO_DIV, "Division by zero."
                                )
                            )
                        else:
                            op = ops.get(token.value)
                            if op:
                                stack.append(op(a, b))
                            else:
                                raise NotImplementedError(
                                    f" Operator '{token.value}' is not implemented"
                                )
                    elif token.type == "FUNC" and token.subtype == "OPEN":
                        raise NotImplementedError()

                if len(stack) != 1:
                    raise ValueError(
                        "Formula evaluation error: too many values remaining."
                    )

                return stack.pop().value

            # evaluate_rpn.inputs = inputs_set
            evaluate_rpn.__setattr__("inputs", inputs_set)
            return evaluate_rpn

    return None
