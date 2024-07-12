from __future__ import annotations

from tolstack.StackTree import TreeNode

from tolstack.StackDim import StackDim

from tolstack.StackTypes import get_eval_from_code

from tolstack.StackUtils import parse_string_to_numeric, is_numeric_string

from typing import Dict


class StackExpr:
    def __init__(
        self,
        key: str,
        expression: str,
        lower: float,
        upper: float,
        method: str,
        root: TreeNode,
        note: str = None,
    ) -> None:
        self.key = key
        self.expr = expression
        self.lower = lower
        self.upper = upper
        self.method = get_eval_from_code(method)
        self.root = root
        self.note = note

    def __str__(self) -> str:
        return f"{self.expr} {self.note}"

    def evaluate(self, value_map=None):
        self._setValueOrError(value_map)

        return self._evaluate(self.root)

    def derivative(self, key, value_map=None) -> float:
        self._setValueOrError(value_map)

        nom, partial = self._evaluateDerivative(self.root, key)

        return partial

    def sensitivities(self, value_map=None) -> Dict[str, float]:
        self._setValueOrError(value_map)

        sensitivities = {}
        variables = self.referenced_values()

        for var in variables:
            partial = self.derivative(var)
            sensitivities[var] = partial

        return sensitivities

    def contributions(self, value_map=None) -> Dict[str, float]:
        self._setValueOrError(value_map)

        base = self.evaluate()

        contributions = {}
        variables = self.referenced_values()

        for var in variables:
            mod = self._evaluate_ideal(self.root, var)
            var_dim = self.value_map[var]

            if var_dim.range() == 0:
                contributions[var] = 0
            else:
                contributions[var] = (base.range() - mod.range()) / 2

        return contributions

    def expand(self):
        return self._format_tree(self.root)

    def referenced_values(self):
        return sorted(self._referenced_values(self.root))

    def set_value_map(self, value_map):
        self.value_map = value_map

    def _evaluate(self, node):
        # base case, node refers to a StackDim input variable or scalar
        if node.left is None and node.right is None:
            return self._getLeafValue(node.key)

        _left = self._evaluate(node.left) if node.left else None
        _right = self._evaluate(node.right) if node.right else None

        match node.key:
            case "+":
                return _left + _right
            case "-":
                return _left - _right
            case "*":
                return _left * _right
            case "/":
                return _left / _right
            case "u-":
                return -_right
            case _:
                raise ValueError(
                    f"Error computing '{node.key}' when evaluating expression, operation not defined."
                )

    def _evaluateDerivative(self, node, key) -> tuple[float, float]:
        # base case, node refers to a StackDim input variable or scalar
        if node.left is None and node.right is None:
            value = self._getLeafValue(node.key)

            if not isinstance(value, StackDim):
                # scalars always have 0 derivative
                return (value, 0)

            nom = value.center(self.method)

            if key != value.key:
                return (nom, 0)
            else:
                return (nom, 1)

        _left, _dleft = self._evaluateDerivative(node.left, key) if node.left else None
        _right, _dright = (
            self._evaluateDerivative(node.right, key) if node.right else None
        )

        match node.key:
            case "+":
                return (_left + _right, _dleft + _dright)
            case "-":
                return (_left - _right, _dleft - _dright)
            case "*":
                # product rule
                return (_left * _right, _left * _dright + _right * _dleft)
            case "/":
                # low dhigh minus high dlow, square the bottom and away we go
                return (
                    _left / _right,
                    (_right * _dleft - _left * _dright) / (_right**2),
                )
            case "u-":
                return (-_right, -_dright)
            case _:
                raise ValueError(
                    f"Error computing '{node.key}' when evaluating derivative, operation not defined."
                )

    def _evaluate_ideal(self, node, key):
        # base case, node refers to a StackDim input variable or scalar
        if node.left is None and node.right is None:
            value = self._getLeafValue(node.key)

            if not isinstance(value, StackDim):
                # scalars always ideal
                return value

            if key != value.key:
                return value
            else:
                return value.ideal()

        _left = self._evaluate_ideal(node.left, key) if node.left else None
        _right = self._evaluate_ideal(node.right, key) if node.right else None

        match node.key:
            case "+":
                return _left + _right
            case "-":
                return _left - _right
            case "*":
                return _left * _right
            case "/":
                return _left / _right
            case "u-":
                return -_right
            case _:
                raise ValueError(
                    f"Error computing '{node.key}' when evaluating contribution, operation not defined."
                )

    def _format_tree(self, node):
        if node.left is None and node.right is None:
            return node.key

        _left = self._format_tree(node.left) if node.left else None
        _right = self._format_tree(node.right) if node.right else None

        if _left:
            return "(" + _left + " " + node.key + " " + _right + ")"
        else:
            match node.key:
                case "u-":
                    return "-" + _right
                case _:
                    raise ValueError(
                        f"Error computing '{node.key}' when formatting tree, operation not defined."
                    )

    def _referenced_values(self, node):
        if node.left is None and node.right is None:
            return {node.key} if node.key in self.value_map else set()

        _left = self._referenced_values(node.left) if node.left else set()
        _right = self._referenced_values(node.right) if node.right else set()

        return _left | _right

    def _getLeafValue(self, key):
        if key in self.value_map:
            return self.value_map[key]

        if is_numeric_string(key):
            return parse_string_to_numeric(key)

        raise ValueError(f"Evaluation of {self.key}: invalid leaf token {key}.")

    def _setValueOrError(self, value_map):
        if value_map is not None:
            self.value_map = value_map

        if self.value_map is None:
            raise RuntimeError(
                f"Cannot evaluate expression {self.key} without map of defined values."
            )
