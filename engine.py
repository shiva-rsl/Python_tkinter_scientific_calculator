"""Expression engine for the scientific calculator.

Display text is normalized, checked with the AST, then evaluated with a
math-only namespace (no builtins). `%` means percent: `50%` → `0.5`.
"""

from __future__ import annotations

import ast
import math
import re
from typing import Callable


class CalculatorError(Exception):
    """User-facing evaluation error."""


_FUNCTION_NAMES = (
    "log10",
    "log2",
    "sinh",
    "cosh",
    "tanh",
    "sqrt",
    "exp",
    "abs",
    "sin",
    "cos",
    "tan",
    "log",
    "ln",
    "factorial",
)

_ALLOWED_FUNCS = {
    "sin",
    "cos",
    "tan",
    "sinh",
    "cosh",
    "tanh",
    "log",
    "log10",
    "log2",
    "sqrt",
    "exp",
    "abs",
    "factorial",
}

_ALLOWED_NAMES = _ALLOWED_FUNCS | {"pi", "e"}

_ALLOWED_AST = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Constant,
    ast.Load,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.UAdd,
    ast.USub,
    ast.Expr,
)


class CalculatorEngine:
    def __init__(self) -> None:
        self.angle_mode = "DEG"

    def set_angle_mode(self, mode: str) -> None:
        mode = mode.upper()
        if mode not in {"DEG", "RAD"}:
            raise CalculatorError("Angle mode must be DEG or RAD")
        self.angle_mode = mode

    def evaluate(self, expression: str) -> str:
        raw = expression.strip()
        if not raw:
            raise CalculatorError("Enter an expression")

        python_expr = self._normalize(raw)
        self._validate_syntax(python_expr)

        try:
            value = eval(python_expr, {"__builtins__": {}}, self._namespace())  # noqa: S307
        except CalculatorError:
            raise
        except ZeroDivisionError:
            raise CalculatorError("Division by zero") from None
        except OverflowError:
            raise CalculatorError("Number too large") from None
        except ValueError as exc:
            raise CalculatorError("Invalid input for this function") from exc
        except SyntaxError:
            raise CalculatorError("Invalid expression") from None
        except Exception:
            raise CalculatorError("Invalid expression") from None

        return self.format_result(value)

    def format_result(self, value: object) -> str:
        if isinstance(value, int):
            if len(str(abs(value))) > 16:
                return f"{value:.12e}"
            return str(value)
        if isinstance(value, complex):
            raise CalculatorError("Complex results are not supported")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise CalculatorError("Invalid expression")
        if isinstance(value, float) and not math.isfinite(value):
            raise CalculatorError("Undefined result")

        if isinstance(value, int):
            return str(value)

        rounded = round(float(value), 12)
        if abs(rounded - round(rounded)) < 1e-12:
            return str(int(round(rounded)))
        return format(rounded, ".12g")

    def _namespace(self) -> dict[str, object]:
        return {
            "pi": math.pi,
            "e": math.e,
            "sin": self._trig(math.sin),
            "cos": self._trig(math.cos),
            "tan": self._tan,
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "log": self._ln,
            "log10": self._log10,
            "log2": self._log2,
            "sqrt": self._sqrt,
            "exp": math.exp,
            "abs": abs,
            "factorial": self._factorial,
        }

    def _trig(self, func: Callable[[float], float]) -> Callable[[float], float]:
        def wrapped(x: float) -> float:
            return func(math.radians(x) if self.angle_mode == "DEG" else x)

        return wrapped

    def _tan(self, x: float) -> float:
        if self.angle_mode == "DEG":
            shifted = (float(x) - 90.0) % 180.0
            if abs(shifted) < 1e-10 or abs(shifted - 180.0) < 1e-10:
                raise CalculatorError("Tangent is undefined")
            return math.tan(math.radians(x))
        cosine = math.cos(x)
        if abs(cosine) < 1e-15:
            raise CalculatorError("Tangent is undefined")
        return math.tan(x)

    def _ln(self, x: float) -> float:
        if x <= 0:
            raise CalculatorError("ln is only defined for x > 0")
        return math.log(x)

    def _log10(self, x: float) -> float:
        if x <= 0:
            raise CalculatorError("log10 is only defined for x > 0")
        return math.log10(x)

    def _log2(self, x: float) -> float:
        if x <= 0:
            raise CalculatorError("log2 is only defined for x > 0")
        return math.log2(x)

    def _sqrt(self, x: float) -> float:
        if x < 0:
            raise CalculatorError("Square root of a negative number")
        return math.sqrt(x)

    def _factorial(self, x: float) -> int:
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if not isinstance(x, int) or isinstance(x, bool):
            raise CalculatorError("Factorial requires a non-negative integer")
        if x < 0:
            raise CalculatorError("Factorial requires a non-negative integer")
        if x > 170:
            raise CalculatorError("Number too large")
        return math.factorial(x)

    def _normalize(self, expression: str) -> str:
        expr = expression.replace(" ", "")
        expr = expr.replace("×", "*").replace("÷", "/")
        expr = expr.replace("√", "sqrt")
        expr = expr.replace("π", "(pi)")
        expr = expr.replace("ln(", "log(")

        expr = self._apply_postfix(expr, "!", "factorial")
        expr = self._apply_postfix(expr, "%", None)
        expr = self._replace_euler_constant(expr)
        expr = self._add_implicit_multiplication(expr)
        expr = expr.replace("^", "**")
        return expr

    def _replace_euler_constant(self, expr: str) -> str:
        return re.sub(r"(?<![A-Za-z0-9._])e(?![A-Za-z0-9_])", "(e)", expr)

    def _apply_postfix(self, expr: str, symbol: str, func_name: str | None) -> str:
        guard = 0
        while symbol in expr:
            guard += 1
            if guard > 500:
                raise CalculatorError("Invalid expression")
            idx = expr.find(symbol)
            operand, start = self._extract_left_operand(expr, idx)
            if func_name is None:
                replacement = f"(({operand})/100)"
            else:
                replacement = f"{func_name}({operand})"
            expr = expr[:start] + replacement + expr[idx + len(symbol) :]
        return expr

    def _extract_left_operand(self, expr: str, op_index: int) -> tuple[str, int]:
        i = op_index - 1
        if i < 0:
            raise CalculatorError("Invalid expression")

        if expr[i] == ")":
            depth = 0
            j = i
            while j >= 0:
                if expr[j] == ")":
                    depth += 1
                elif expr[j] == "(":
                    depth -= 1
                    if depth == 0:
                        k = j - 1
                        while k >= 0 and (expr[k].isalnum() or expr[k] == "_"):
                            k -= 1
                        return expr[k + 1 : i + 1], k + 1
                j -= 1
            raise CalculatorError("Unmatched parentheses")

        j = i
        if expr[j].isdigit() or expr[j] == ".":
            while j >= 0 and (expr[j].isdigit() or expr[j] in ".eE"):
                j -= 1
            if j >= 0 and expr[j] in "+-" and j - 1 >= 0 and expr[j - 1] in "eE":
                j -= 1
                while j >= 0 and (expr[j].isdigit() or expr[j] == "."):
                    j -= 1
            return expr[j + 1 : i + 1], j + 1

        if expr[j].isalpha() or expr[j] == "_":
            while j >= 0 and (expr[j].isalnum() or expr[j] == "_"):
                j -= 1
            return expr[j + 1 : i + 1], j + 1

        raise CalculatorError("Invalid expression")

    def _add_implicit_multiplication(self, expr: str) -> str:
        protected, placeholders = self._protect_functions(expr)

        protected = re.sub(r"\)\s*\(", ")*(", protected)
        protected = re.sub(r"\)\s*(?=[\dA-Za-z_])", ")*", protected)
        protected = re.sub(r"(\d)\s*\(", r"\1*(", protected)
        protected = re.sub(r"(\d)\s*(?=__F)", r"\1*", protected)
        protected = re.sub(r"(\d)\s*(?=[A-Za-z])", r"\1*", protected)
        protected = re.sub(r"(__F\d+__)\s+(?=[A-Za-z_])", r"\1*", protected)

        return self._unprotect_functions(protected, placeholders)

    def _protect_functions(self, expr: str) -> tuple[str, dict[str, str]]:
        placeholders: dict[str, str] = {}
        protected = expr
        for index, name in enumerate(_FUNCTION_NAMES):
            token = f"__F{index}__"
            placeholders[token] = name
            protected = protected.replace(f"{name}(", f"{token}(")
        return protected, placeholders

    def _unprotect_functions(self, expr: str, placeholders: dict[str, str]) -> str:
        for token, name in placeholders.items():
            expr = expr.replace(f"{token}(", f"{name}(")
        return expr

    def _validate_syntax(self, python_expr: str) -> None:
        if python_expr.count("(") != python_expr.count(")"):
            raise CalculatorError("Unmatched parentheses")

        try:
            tree = ast.parse(python_expr, mode="eval")
        except SyntaxError as exc:
            raise CalculatorError("Invalid expression") from exc

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCS:
                    raise CalculatorError("Invalid expression")
                if node.keywords:
                    raise CalculatorError("Invalid expression")
            elif isinstance(node, ast.Name):
                if node.id not in _ALLOWED_NAMES:
                    raise CalculatorError("Invalid expression")
            elif not isinstance(node, _ALLOWED_AST):
                raise CalculatorError("Invalid expression")
