import logging
import typing
from collections import deque
from types import MappingProxyType
from typing import Any, Callable, Dict, List, Mapping, Sequence, Set, Tuple, Union

import mvin.excel_ops as _  # noqa

from mvin import REGISTERED_OPS, Token, TokenError, TokenErrorTypes, TokenFunc
from mvin.functions.excel_lib import DEFAULT_FUNCTIONS

# Operator precedence and associativity
OPERATORS: Mapping[str, Tuple[Union[int, float], str]] = MappingProxyType(
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
    proposed_functions: Dict[
        str, Tuple[Union[List, None], Callable]
    ] = DEFAULT_FUNCTIONS,
    registered_ops: Dict[str, Callable[[Token, Token], Token]] = REGISTERED_OPS,
) -> Union[Callable[[Dict[str, Any]], Any], None]:
    if isinstance(tokens, Sequence):
        ops = MappingProxyType(dict(registered_ops))

        copied_functions: Dict[str, Tuple[Union[List, None], Callable]] = {}
        for func_name, (defaults, func_callable) in dict(proposed_functions).items():
            copied_defaults = list(defaults) if defaults is not None else None
            copied_functions[func_name] = (copied_defaults, func_callable)
        functions = MappingProxyType(copied_functions)

        def infix_to_rpn(
            tokens: Sequence[Token],  # tokens from the tokenizer
            functions: Mapping[str, Tuple[Union[List, None], Callable]],
        ) -> Tuple[List[Union[Token, int, None]], Set[str]]:
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
            output: List[Union[Token, int, None]] = []
            op_stack: deque[Token] = deque()
            arg_stack: deque[int] = (
                deque()
            )  # Keeps track of argument counts for nested function calls
            open_parens = 0

            inputs: Set[str] = set()

            filtered_tokens = [x for x in tokens if x is None or x.type != "WHITE-SPACE"]

            for i, token in enumerate(filtered_tokens):
                prev_token = filtered_tokens[i - 1] if i > 0 else None
                logging.debug(
                    f"--------\noutput: {output}\nop_stack: {op_stack}\narg_count: {arg_stack}\ntoken: {token}"
                )
                if token is None:
                    raise SyntaxError(f"Unexpected None value found at position {i}.")
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
                    # op_stack.append(func_name)
                    op_stack.append(token)
                    arg_stack.append(
                        1
                    )  # Start with one argument for this instance of the function

                    op_stack.append(TokenFunc("("))
                    open_parens += 1

                elif token.value == "(":  # Left parenthesis
                    if prev_token and prev_token.type == "OPERAND":
                        raise SyntaxError(
                            f"Missing operator before '(' at position {i}."
                        )
                    op_stack.append(token)
                    open_parens += 1

                elif token.value == ")":  # Right parenthesis
                    open_parens -= 1
                    if open_parens < 0:
                        raise SyntaxError(
                            f"Unexpected `)` at position {i} (too many closing parentheses)."
                        )

                    # Ensure trailing empty argument handling
                    last_token = prev_token
                    logging.debug(f"last_token: {last_token}")
                    if last_token:
                        if last_token.type == "FUNC" and last_token.subtype == "OPEN":
                            arg_stack[-1] = 0

                        elif last_token.value == ",":
                            output.append(None)  # Handle missing last argument

                    while op_stack and op_stack[-1].value != "(":
                        output.append(op_stack.pop())

                    if not op_stack:
                        raise SyntaxError(f"Unmatched `)` at position {i}.")
                    op_stack.pop()  # Remove '('

                    if op_stack and op_stack[-1].type == "FUNC":
                        #!!! DESIGN DECISION
                        #
                        # Support closing parenthesis, even when is not of type='FUNC' --> display warning
                        if token.type != "FUNC":
                            logging.warning(
                                f"Expected token of type:`FUNC` and subtype:`CLOSE`, but found token of type:`{token.type}`"
                            )
                        func = op_stack.pop()
                        func_name = func.value
                        arg_count = arg_stack.pop()  # Use dynamic argument count

                        #!!! DESIGN DECISION
                        #
                        # arg_count full validation: We are filling the missing part of the arguments
                        #
                        required_args, _ = functions[func_name]
                        if required_args is not None:
                            required_args_count = len(required_args)

                            if required_args_count < arg_count:
                                raise SyntaxError(
                                    f"Function `{func_name}` expects {required_args_count} arguments but got {arg_count}."
                                )

                            # copy defaults to stack if not None
                            # print(
                            #     f" --> arg_count:{arg_count} required_args_count:{required_args_count}"
                            # )
                            arg_index = arg_count
                            while arg_index < required_args_count:
                                default_arg = required_args[arg_index]
                                # print(
                                #     f"   --> arg_index:{arg_index} default_arg: {default_arg}"
                                # )
                                if default_arg is not None:
                                    output.append(default_arg)
                                else:
                                    raise SyntaxError(
                                        f"Missing required argument at {arg_index} for function `{func_name}`"
                                    )
                                arg_index += 1
                            arg_count = required_args_count

                        #!!! DESIGN DECISION
                        #
                        # There are 2 ways to go to correct the arg_count bug:
                        #  - Use the stack to store the arg_count:
                        #    * append the arg_count first as int (and in the execute part, read it from stack)
                        #    * append the TokenFunc
                        #
                        #    > This option pollutes the stack by mixing types
                        #    > There is a possibility to have more dynamic variable arguments calling by putting
                        #      the value in the stack
                        #
                        #  - Use the output to store the arg_count and read it directly when execute
                        #    * appent the TokenFunc
                        #    * append the arg_count as int (and read it just after the TokenFunc, and it will never reach the Token evaluation)
                        #
                        #    > This options requires an additional index to track the rpn_tokens' position
                        #
                        #  I preferred the non pullution version (the second one)

                        # output.append(TokenFunc(func_name))
                        output.append(func)
                        output.append(arg_count)

                elif token.type == "OPERATOR-INFIX":
                    if i == 0 or (
                        prev_token
                        and (
                            (
                                prev_token.type == "OPERATOR-INFIX"
                                and prev_token.value != ")"
                                and prev_token.subtype != "CLOSE"
                            )
                            or prev_token.value == "("
                        )
                    ):
                        raise SyntaxError(
                            f"Unexpected operator `{token}` at position {i}."
                        )
                    token_value = token.value
                    while (
                        op_stack
                        and op_stack[-1].value in OPERATORS
                        and (
                            (
                                OPERATORS[token_value][1] == "L"
                                and OPERATORS[token_value][0]
                                <= OPERATORS[op_stack[-1].value][0]
                            )
                            or (
                                OPERATORS[token_value][1] == "R"
                                and OPERATORS[token_value][0]
                                < OPERATORS[op_stack[-1].value][0]
                            )
                        )
                    ):
                        output.append(op_stack.pop())  # TODO Improve test coverage
                    op_stack.append(token)

                elif (
                    token.type == "SEP" and token.subtype == "ARG"
                ):  # token.value == ',':
                    if prev_token is None:
                        raise SyntaxError(
                            f"Unexpected separator `{token}` at position {i}."
                        )

                    if prev_token.subtype == "OPEN" or prev_token.value == ",":
                        output.append(None)  # Handle missing argument

                    while op_stack and op_stack[-1].value != "(":
                        output.append(op_stack.pop())

                    if arg_stack:
                        arg_stack[-1] += (
                            1  # Increase count for the current function call
                        )

                # elif token.type == "WHITE-SPACE":
                #     pass

                else:
                    raise SyntaxError(f"Unrecognized token `{token}` at position {i}.")

            if open_parens > 0:
                raise SyntaxError("Unmatched `(` (missing closing parenthesis).")

            while op_stack:
                if op_stack[-1].value == "(":
                    raise SyntaxError("Unmatched `(` in expression.")
                output.append(op_stack.pop())

            return output, inputs

        rpn_tokens, inputs = infix_to_rpn(tokens, functions)
        # print(f"rpn_tokens: {rpn_tokens}")

        def execute_func(
            rpn_tokens: Sequence[Union[Token, int, None]], inputs_set: Set[str]
        ) -> Callable[[Dict[str, typing.Any]], Any]:
            def evaluate_rpn(
                inputs: Union[Dict[str, typing.Any], None] = None,
            ) -> typing.Any:
                provided_inputs = {} if inputs is None else dict(inputs)
                immutable_inputs: Mapping[str, Any] = MappingProxyType(provided_inputs)

                stack = deque()

                i = 0  # Token index for argument count retrieval

                while i < len(rpn_tokens):
                    token = rpn_tokens[i]
                    i += 1  # Move to the next token
                    # print(token)

                    if token is None:
                        # raise ValueError(f"Unexpected None at position {i}")
                        stack.append(token)
                    elif isinstance(token, int):
                        raise ValueError(
                            f"Unexpected token (int: {token}) at position {i} "
                        )
                    elif token.type == "OPERAND":
                        if token.subtype != "RANGE":
                            stack.append(token)
                        else:
                            if token.value in immutable_inputs:
                                stack.append(immutable_inputs[token.value])
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

                        logging.debug(
                            f"interpreter: applying op: {token.value} with a: {a.value} b: {b.value}"
                        )

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
                                    f"Operator '{token.value}' is not implemented"
                                )
                    elif token.type == "FUNC" and token.subtype == "OPEN":
                        func_name = token.value

                        if i >= len(rpn_tokens):
                            raise ValueError(
                                f"Missing argument count for function `{func_name}`."
                            )

                        arg_count = rpn_tokens[
                            i
                        ]  # Read argument count from tokens, not stack
                        i += 1  # Move to next token after argument count

                        if isinstance(arg_count, int):
                            args = [
                                stack.pop() if stack else None for _ in range(arg_count)
                            ][::-1]
                            # print(f"`{func_name}`-> args: {args}")

                            # Get function default values
                            func_defaults, func_callable = functions[func_name]

                            if func_defaults is not None:
                                required_args_count = len(func_defaults)
                                if len(args) != required_args_count:
                                    raise ValueError(
                                        f"Function `{token}` expects {required_args_count} arguments but got {len(args)}."
                                    )
                                arg_index = 0
                                while arg_index < required_args_count:
                                    default_value = func_defaults[arg_index]
                                    # print(
                                    #     f" *-> Eval#{func_name} :: {arg_index} | {args[arg_index]} | {default_value}"
                                    # )
                                    if (
                                        default_value is None
                                        and args[arg_index] is None
                                    ):
                                        raise ValueError(
                                            f"Missing required argument at {arg_index} for function `{func_name}`"
                                        )
                                    arg_index += 1

                            func_result = func_callable(*args)
                            # print(f"`{func_name}`-> result: {func_result}")
                            if func_result:
                                stack.append(func_result)
                        else:
                            raise RuntimeError(
                                f"Expected an interger arg_count for function `{func_name}`'s arg_count, but found {arg_count}"
                            )

                if len(stack) != 1:
                    raise ValueError(
                        "Formula evaluation error: too many values remaining."
                    )

                return stack.pop().value

            evaluate_rpn.__setattr__("inputs", inputs_set)
            return evaluate_rpn

        return execute_func(rpn_tokens, inputs)
    return None
