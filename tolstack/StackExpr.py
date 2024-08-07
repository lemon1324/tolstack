from __future__ import annotations

from tolstack.StackTree import TreeNode

from tolstack.StackDim import StackDim

from tolstack.StackTypes import get_eval_from_code

from tolstack.StackUtils import (
    parse_string_to_numeric,
    is_numeric_string,
    get_precedence,
    is_tree_operator,
    is_higher_precedence,
    needs_grouping,
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

    def evaluate(self, value_map=None) -> StackDim:
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
            mod = self._evaluate(self.root, var)
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

    def _evaluate(self, node, ideal_key=None):
        # base case, node refers to a StackDim input variable or scalar
        if node.left is None and node.right is None:
            return self._getLeafValue(node.key, ideal_key)

        _left = self._evaluate(node.left, ideal_key) if node.left else None
        _right = self._evaluate(node.right, ideal_key) if node.right else None

        return self._apply_operation(node.key, _left, _right)

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

        return self._apply_operation(node.key, _left, _right, _dleft, _dright)

    def _apply_operation(self, op, left, right, dleft=None, dright=None):
        operations = {
            "+": (lambda l, r: l + r, lambda l, r, dl, dr: (l + r, dl + dr)),
            "-": (lambda l, r: l - r, lambda l, r, dl, dr: (l - r, dl - dr)),
            "*": (
                lambda l, r: l * r,
                # product rule
                lambda l, r, dl, dr: (l * r, l * dr + r * dl),
            ),
            "/": (
                lambda l, r: l / r,
                # low dhigh minus high dlow, square the bottom and away we go
                lambda l, r, dl, dr: (l / r, (r * dl - l * dr) / (r**2)),
            ),
            "^": (
                lambda l, r: l**r,
                lambda l, r, dl, dr: (l**r, l**r * (dl * (r / l) + dr * np.log(l))),
            ),
            "u-": (lambda _, r: -r, lambda _, r, __, dr: (-r, -dr)),
            "sin": (
                lambda _, r: StackDim.sin(r),
                lambda _, r, __, dr: (np.sin(r), np.cos(r) * dr),
            ),
            "sind": (
                lambda _, r: StackDim.sind(r),
                lambda _, r, __, dr: (
                    np.sin(r * np.pi / 180),
                    np.cos(r * np.pi / 180) * (dr * np.pi / 180),
                ),
            ),
            "cos": (
                lambda _, r: StackDim.cos(r),
                lambda _, r, __, dr: (np.cos(r), -np.sin(r) * dr),
            ),
            "cosd": (
                lambda _, r: StackDim.cosd(r),
                lambda _, r, __, dr: (
                    np.cos(r * np.pi / 180),
                    -np.sin(r * np.pi / 180) * (dr * np.pi / 180),
                ),
            ),
            "tan": (
                lambda _, r: StackDim.tan(r),
                lambda _, r, __, dr: (
                    np.tan(r),
                    ((4 * np.cos(r) ** 2) / (np.cos(2 * r) + 1) ** 2) * dr,
                ),
            ),
            "tand": (
                lambda _, r: StackDim.tand(r),
                lambda _, r, __, dr: (
                    np.tan(r * np.pi / 180),
                    (
                        (4 * np.cos(r * np.pi / 180) ** 2)
                        / (np.cos(2 * r * np.pi / 180) + 1) ** 2
                    )
                    * (dr * np.pi / 180),
                ),
            ),
        }

        try:
            operation, derivative_operation = operations[op]
            if dleft is not None and dright is not None:
                return derivative_operation(left, right, dleft, dright)
            else:
                return operation(left, right)
        except KeyError:
            raise ValueError(
                f"Error computing '{op}' when evaluating expression, operation not defined."
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
            if is_higher_precedence(parent_key, child_key):
                return f"({child_str})"
            elif needs_grouping(parent_key, child_key):
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

    def _getLeafValue(self, key, ideal_key=None):
        if key in self.value_map:
            value = self.value_map[key]
            if not isinstance(value, StackDim):
                return value
            if ideal_key and ideal_key == key:
                return value.ideal(self.method)
            return value

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
