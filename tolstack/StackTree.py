from tolstack.StackUtils import is_variable, infix_to_rpn
import sys


class TreeNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


class TreeParser:
    def __init__(self, values) -> None:
        self.value_map = values
        self.expression_map = dict()

    def construct_tree(self, key, raw_expression):
        rpn_expression = infix_to_rpn(raw_expression)
        root = self._construct_expression_tree(key, rpn_expression)
        return root

    def _construct_expression_tree(self, key, rpn_expression):
        stack = []

        for token in rpn_expression:
            if is_variable(token):
                if token in self.value_map:
                    stack.append(TreeNode(token))
                elif token in self.expression_map:
                    stack.append(self.expression_map[token])
                else:
                    sys.exit(
                        f"Error adding node for {token}, not defined in the value or expression map."
                    )
            else:  # token is an operator
                node = TreeNode(token)
                node.right = stack.pop()
                node.left = stack.pop()
                stack.append(node)

        self.expression_map[key] = stack[0]
        return stack[0]


def inorder_traversal(node):
    if not node:
        return ""
    left = inorder_traversal(node.left)
    right = inorder_traversal(node.right)
    if node.left and node.right:
        return f"({left} {node.operator} {right})"
    return f"{node.value}"


def print_tree(node):
    if not node:
        return ""
    print_tree(node.left)
    print_tree(node.right)
    if node.left and node.right:
        print(
            f"Oper node, key: {node.key}, value: {node.computed_value}, left: {node.left.key}, right: {node.right.key}"
        )
    else:
        print(f"  Leaf node, key: {node.key}, value: {node.computed_value}")


if __name__ == "__main__":
    # Example usage
    expression = "3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3"
    print(expression)

    # tree_root = construct_expression_tree(infix_to_rpn(expression))
    # print_tree(tree_root)
