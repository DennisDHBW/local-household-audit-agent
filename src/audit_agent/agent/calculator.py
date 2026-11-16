"""Safe arithmetic for the ``calculate`` tool: AST walk instead of ``eval`` (concept.md, 7.2).

Only numbers, ``+ - * / **``, unary signs and parentheses are allowed. Names, calls,
attributes and everything else are rejected before anything is computed. The numbers are
``Decimal`` values, so ``0.395 - 0.382`` is exactly ``0.013`` and not ``0.01300000000000001``.
"""

from __future__ import annotations

import ast
import operator
import re
from collections.abc import Callable
from decimal import Decimal

MAX_EXPRESSION_CHARS = 200
MAX_NODES = 60
MAX_EXPONENT = 10
RESULT_DECIMALS = 6

_BINARY: dict[type[ast.operator], Callable[[Decimal, Decimal], Decimal]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_GERMAN_THOUSANDS = re.compile(r"\b\d{1,3}(?:\.\d{3})+(?=,\d)")
_GERMAN_DECIMAL = re.compile(r"(?<=\d),(?=\d)")
_CURRENCY = re.compile(r"€|\bEUR\b", re.IGNORECASE)


class CalculationError(ValueError):
    """The expression is not allowed or cannot be computed (message goes to the model)."""


def normalize_expression(expression: str) -> str:
    """Be liberal in what is accepted (Postel): ``3,5 * 2 €`` -> ``3.5 * 2``.

    A point is a thousands separator only before a decimal comma (``1.963,28`` -> ``1963.28``);
    ``1.963`` alone stays a decimal number, because it could be either.
    """
    text = _CURRENCY.sub("", expression).strip()
    text = _GERMAN_THOUSANDS.sub(lambda match: match.group().replace(".", ""), text)
    return _GERMAN_DECIMAL.sub(".", text)


def _evaluate(node: ast.AST) -> Decimal:
    if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
        if isinstance(node.value, bool):
            raise CalculationError("Wahrheitswerte sind nicht erlaubt")
        return Decimal(str(node.value))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub | ast.UAdd):
        value = _evaluate(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp):
        left, right = _evaluate(node.left), _evaluate(node.right)
        if isinstance(node.op, ast.Pow):
            if right != right.to_integral_value() or abs(right) > MAX_EXPONENT:
                raise CalculationError(f"Exponent muss eine ganze Zahl bis {MAX_EXPONENT} sein")
            return left ** int(right)
        function = _BINARY.get(type(node.op))
        if function is None:
            raise CalculationError(f"Operator {type(node.op).__name__} ist nicht erlaubt")
        return function(left, right)
    raise CalculationError(f"{type(node).__name__} ist nicht erlaubt (nur Zahlen und + - * / **)")


def calculate(expression: str) -> Decimal:
    """Value of an arithmetic expression, rounded to ``RESULT_DECIMALS`` places."""
    text = normalize_expression(expression)
    if not text:
        raise CalculationError("leerer Ausdruck")
    if len(text) > MAX_EXPRESSION_CHARS:
        raise CalculationError(f"Ausdruck länger als {MAX_EXPRESSION_CHARS} Zeichen")
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError as error:
        raise CalculationError(f"kein gültiger Ausdruck: {text!r}") from error
    if sum(1 for _ in ast.walk(tree)) > MAX_NODES:
        raise CalculationError("Ausdruck zu verschachtelt")
    try:
        result = _evaluate(tree.body)
        return result.quantize(Decimal(1).scaleb(-RESULT_DECIMALS))
    except ArithmeticError as error:
        raise CalculationError("Division durch null oder Zahl außerhalb des Bereichs") from error


def format_result(value: Decimal) -> str:
    """``1189.000000`` -> ``1189``; ``0.013000`` -> ``0.013`` (plain notation, no exponent)."""
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text
