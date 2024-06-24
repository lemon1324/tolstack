from __future__ import annotations

from tolstack.StackTree import TreeNode

from tolstack.StackTypes import get_eval_from_code

import sys


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
        if value_map is not None:
            self.value_map = value_map

        if self.value_map is None:
            sys.exit(
                f"Cannot evaluate expression {self.key} without map of defined values."
            )

        return self._evaluate(self.root)

    def expand(self):
        return self._format_tree(self.root)

    def referenced_values(self):
        return self._referenced_values(self.root)

    def set_value_map(self, value_map):
        self.value_map = value_map

    def _evaluate(self, node):
        # base case, node refers to a StackDim input variable
        if node.left is None and node.right is None:
            return self.value_map[node.key]

        _left = self._evaluate(node.left)
        _right = self._evaluate(node.right)

        match node.key:
            case "+":
                return _left + _right
            case "-":
                return _left - _right
            case _:
                sys.exit(f"Error computing '{node.key}', operation not defined.")

    def _format_tree(self, node):
        if node.left is None and node.right is None:
            return node.key

        _left = self._format_tree(node.left)
        _right = self._format_tree(node.right)

        return "(" + _left + " " + node.key + " " + _right + ")"

    def _referenced_values(self, node):
        if node.left is None and node.right is None:
            return {node.key}

        _left = self._referenced_values(node.left)
        _right = self._referenced_values(node.right)

        return _left | _right
