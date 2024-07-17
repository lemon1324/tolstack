from __future__ import annotations

from tolstack.StackTree import TreeNode

from tolstack.StackDim import StackDim

from tolstack.StackTypes import get_eval_from_code

from tolstack.StackUtils import (
    parse_string_to_numeric,
    is_numeric_string,
    get_precedence,
    is_tree_operator,
)

from typing import Dict

import numpy as np


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
                # set contributions to zero if the statistical model happens to suggest
                # the tighter tolerance actually hurt overall tolerance, which should not be possible.
                # If this happens, it is a result of limitations in the Monte Carlo simulation for a
                # statistical analysis.
                contributions[var] = max(
                    (base.range(self.method) - mod.range(self.method)) / 2, 0
                )

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
            case "^":
                return _left**_right
            case "u-":
                return -_right
            case "sin":
                return StackDim.sin(_right)
            case "cos":
                return StackDim.cos(_right)
            case "tan":
                return StackDim.tan(_right)
            case "sind":
                return StackDim.sind(_right)
            case "cosd":
                return StackDim.cosd(_right)
            case "tand":
                return StackDim.tand(_right)
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

        _left, _dleft = (
            self._evaluateDerivative(node.left, key) if node.left else (None, None)
        )
        _right, _dright = (
            self._evaluateDerivative(node.right, key) if node.right else (None, None)
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
            case "^":
                return (
                    _left**_right,
                    _left**_right
                    * (_dleft * (_right / _left) + _dright * np.log(_left)),
                )
            case "u-":
                return (-_right, -_dright)
            case "sin":
                return (np.sin(_right), np.cos(_right) * _dright)
            case "sind":
                return (
                    np.sin(_right * np.pi / 180),
                    np.cos(_right * np.pi / 180) * (_dright * np.pi / 180),
                )
            case "cos":
                return (np.cos(_right), -np.sin(_right) * _dright)
            case "cosd":
                return (
                    np.cos(_right * np.pi / 180),
                    -np.sin(_right * np.pi / 180) * (_dright * np.pi / 180),
                )
            case "tan":
                return (
                    np.tan(_right),
                    ((4 * np.cos(_right) ** 2) / (np.cos(2 * _right) + 1) ** 2)
                    * _dright,
                )
            case "tand":
                _rd = _right * np.pi / 180
                _drd = _dright * np.pi / 180
                return (
                    np.tan(_rd),
                    ((4 * np.cos(_rd) ** 2) / (np.cos(2 * _rd) + 1) ** 2) * _drd,
                )
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
                return value.ideal(self.method)

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
            case "^":
                return _left**_right
            case "u-":
                return -_right
            case "sin":
                return StackDim.sin(_right)
            case "sind":
                return StackDim.sind(_right)
            case "cos":
                return StackDim.cos(_right)
            case "cosd":
                return StackDim.cosd(_right)
            case "tan":
                return StackDim.tan(_right)
            case "tand":
                return StackDim.tand(_right)
            case _:
                raise ValueError(
                    f"Error computing '{node.key}' when evaluating contribution, operation not defined."
                )

    def _format_tree(self, node):
        if (
            node.left is None and node.right is None
        ):  # This is a leaf node, just return the key
            return node.key

        # Format left and right children
        _left = self._format_tree(node.left) if node.left else None
        _right = self._format_tree(node.right) if node.right else None

        if _left:
            _left_grouped = self._group_child(_left, node.left.key, node.key)
            _right_grouped = self._group_child(_right, node.right.key, node.key)

            return f"{_left_grouped} {node.key} {_right_grouped}"
        else:
            return self._handle_unary_operator(node.key, _right)

    def _group_child(self, child_str, child_key, parent_key):
        if is_tree_operator(child_key):
            if get_precedence(child_key) < get_precedence(parent_key):
                return f"({child_str})"
        return child_str

    def _handle_unary_operator(self, operator, operand):
        match operator:
            case "u-":
                return f"-{operand}"
            case "sin":
                return f"sin({operand})"
            case "sind":
                return f"sind({operand})"
            case "cos":
                return f"cos({operand})"
            case "cosd":
                return f"cosd({operand})"
            case "tan":
                return f"tan({operand})"
            case "tand":
                return f"tand({operand})"
            case _:
                raise ValueError(
                    f"Error computing '{operator}' when formatting tree, unary operation {operator} not defined."
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
