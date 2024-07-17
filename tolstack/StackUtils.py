import re
import numpy as np
from math import isclose

# Precedence levels of operators
PRECEDENCE = {
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
    "^": 3,
    "u-": 10,
    "sin": 10,
    "cos": 10,
    "tan": 10,
    "sind": 10,
    "cosd": 10,
    "tand": 10,
}
OPERATORS = "+-*/^"
TRIG_OPERATORS = ["sin", "cos", "tan", "sind", "cosd", "tand"]
INFIX_UNARY_OPERATORS = ["-"]
RPN_UNARY_OPERATORS = ["u-"]
SYMBOLS = "(" + OPERATORS

# Define a regex pattern for operators, parentheses, and operands
TOKEN_RE = r"(\b\w+\b|[()+\-*/^])"

# Define a regex pattern for variables (dimensions, expressions, etc.)
VARIABLE_RE = r"\w+"


# Given an expression containing values and operators, tokenize it, stripping whitespace
def tokenize(expression):
    # Use the findall method from the re module to extract all tokens
    tokens = re.findall(TOKEN_RE, expression)

    return tokens


# Helper function to determine if a token is an operator in an infix context
def is_operator(token):
    return token in OPERATORS or token in TRIG_OPERATORS


# If the given token can be a unary operator in an infix context
def can_be_unary_operator(token):
    return token in INFIX_UNARY_OPERATORS or token in TRIG_OPERATORS


# determines if an operator is a unary operator in an RPN context
def is_unary_operator(token):
    return token in RPN_UNARY_OPERATORS or token in TRIG_OPERATORS


# determines if a token is a variable in an infix context
def is_variable(token):
    return re.fullmatch(VARIABLE_RE, token) and token not in TRIG_OPERATORS


# Helper function to get precedence of an operator
def get_precedence(op):
    return PRECEDENCE[op]


# Helper function to determine if a token is an operator in an expression tree node
def is_tree_operator(token):
    return token in PRECEDENCE


def word_wrap(text, width, hanging_indent=0):
    """
    Wraps a long string based on the specified width and applies hanging indent,
    preserving the original whitespace except for those replaced by line breaks.

    Parameters:
        text (str): The input string to be wrapped.
        width (int): The maximum width of each line.
        hanging_indent (int): The number of spaces to add as hanging indent for each line.

    Returns:
        str: The word-wrapped string with hanging indents and preserved whitespaces.
    """
    import re

    # Split the text using regex to capture all whitespace
    words = re.split(r"(\s+)", text)

    if not words:
        return ""

    wrapped_lines = []
    current_line = words[0]

    for i in range(1, len(words)):
        word = words[i]
        if len(current_line) + len(word) <= width:
            current_line += word
        else:
            wrapped_lines.append(current_line.rstrip())
            current_line = " " * hanging_indent + word.lstrip()

    wrapped_lines.append(current_line.rstrip())

    return "\n".join(wrapped_lines)


def parse_string_to_numeric(string: str):
    """
    Parses a string and converts it into a numeric value (float).

    Args:
        string (str): The input string to be parsed.

    Returns:
        float or None: Returns a floating-point number if the string can be
                       successfully converted. Returns None if the string is
                       None, cannot be converted to a number, or represents NaN.
    """
    if string is None:
        return None
    try:
        num = float(string)
        return None if np.isnan(num) else num
    except ValueError:
        return None


def is_numeric_string(string: str) -> bool:
    """
    Whether a string can be converted to a float by parse_string_to_numeric.

    Args:
        string (str): The input string to be checked.

    Returns:
        bool: True if the string can be parse, false otherwise.
    """
    if string is None:
        return False
    try:
        num = float(string)
        return False if np.isnan(num) else True
    except ValueError:
        return False


def percent_to_fraction(percentage: str):
    """
    Converts a percentage string to its corresponding fraction.

    Parameters:
    ----------
    percentage : str
        The string representing the percentage (e.g., "75%", "12.5%").

    Returns:
    -------
    float or None
        The fraction corresponding to the given percentage, or None if the input is invalid.
    """
    if percentage is None:
        return None

    try:
        # Check if the last character is '%'
        if percentage[-1] != "%":
            return None

        # Remove the '%' and attempt to convert to a float
        num = float(percentage[:-1])

        # Return the fraction
        return num / 100
    except (ValueError, IndexError):
        return None


def infix_to_rpn(expression):
    # Stack for operators and parentheses
    operator_stack = []
    # Output list for RPN
    output = []

    # Tokenize the input expression (split by spaces for simplicity)
    tokens = tokenize(expression)

    previous_token = None  # To help with identifying unary operators

    for token in tokens:
        if is_variable(token):  # Operand (number or variable)
            output.append(token)
        elif is_operator(token):  # Operator
            if can_be_unary_operator(token) and (
                previous_token is None
                or previous_token in SYMBOLS
                or previous_token in TRIG_OPERATORS
            ):
                # Handle unary operators
                if token == "-":
                    while (
                        operator_stack
                        and operator_stack[-1] != "("
                        and get_precedence(operator_stack[-1]) > get_precedence("u-")
                    ):
                        output.append(operator_stack.pop())
                    operator_stack.append("u-")
                elif token in TRIG_OPERATORS:
                    while (
                        operator_stack
                        and operator_stack[-1] != "("
                        and get_precedence(operator_stack[-1]) > get_precedence(token)
                    ):
                        output.append(operator_stack.pop())
                    operator_stack.append(token)
                else:
                    raise ValueError(
                        f"Cannot process {expression}, unexpected unary operator {token}."
                    )
            else:
                # Handle binary operator
                while (
                    operator_stack
                    and operator_stack[-1] != "("
                    and get_precedence(operator_stack[-1]) >= get_precedence(token)
                ):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
        elif token == "(":  # Left parenthesis
            operator_stack.append(token)
        elif token == ")":  # Right parenthesis
            while operator_stack and operator_stack[-1] != "(":
                output.append(operator_stack.pop())
            operator_stack.pop()  # Discard the left parenthesis

        previous_token = token

    # Pop any remaining operators from the stack
    while operator_stack:
        output.append(operator_stack.pop())

    return output


def addCombination(
    a: tuple[float, float], b: tuple[float, float]
) -> tuple[float, float]:
    """
    Utility function to explicitly compute min/max combinations of tolerances.

        :param a: a 2-tuple of the plus and minus tolerances for a StackDim.
        :param b: a 2-tuple of the plus and minus tolerances for a second StackDim.
        :returns: A 2-tuple containing the plus and minus tolerances of the result of adding the two StackDims.
    """
    # all 4 combinations of tolerances
    sums = np.array([a[0], a[0], a[1], a[1]]) + np.array([b[0], b[1], b[0], b[1]])
    return (max(sums), min(sums))


def subtractCombination(
    a: tuple[float, float], b: tuple[float, float]
) -> tuple[float, float]:
    """
    Utility function to explicitly compute min/max combinations of tolerances.

    Subtracts b from a.

        :param a: a 2-tuple of the plus and minus tolerances for a StackDim.
        :param b: a 2-tuple of the plus and minus tolerances for a second StackDim.
        :returns: A 2-tuple containing the plus and minus tolerances of the result of subtracting b from a.
    """
    # all 4 combinations of tolerances
    sums = np.array([a[0], a[0], a[1], a[1]]) - np.array([b[0], b[1], b[0], b[1]])
    return (max(sums), min(sums))


def mulCombination(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float]:
    """
    Utility function to explicitly compute min/max combinations of tolerances.

        :param a: a 3-tuple of the nominal value, plus, and minus tolerances for a StackDim.
        :param b: a 3-tuple of the nominal value, plus, and minus tolerances for a second StackDim.
        :returns: A 2-tuple containing the plus and minus tolerances of the result of worst-case multiplying the two StackDims.
    """
    nom = a[0] * b[0]
    a_vals = np.array([a[1], a[2]])
    b_vals = np.array([b[1], b[2]])

    # Create all 4 combinations of products
    products = np.array([(a[0] + da) * (b[0] + db) for da in a_vals for db in b_vals])

    deviations = products - nom
    return max(deviations), min(deviations)


def divCombination(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float]:
    """
    Utility function to explicitly compute min/max combinations of tolerances.

        :param a: a 3-tuple of the nominal value, plus, and minus tolerances for a StackDim.
        :param b: a 3-tuple of the nominal value, plus, and minus tolerances for a second StackDim.
        :returns: A 2-tuple containing the plus and minus tolerances of the result of worst-case dividing a by b.
    """
    nom = a[0] / b[0]
    a_vals = np.array([a[1], a[2]])
    b_vals = np.array([b[1], b[2]])

    # Create all 4 combinations of quotients
    quotients = np.array([(a[0] + da) / (b[0] + db) for da in a_vals for db in b_vals])

    deviations = quotients - nom
    return max(deviations), min(deviations)


def expCombination(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float]:
    """
    Utility function to explicitly compute min/max combinations of tolerances.

        :param a: a 3-tuple of the nominal value, plus, and minus tolerances for a StackDim.
        :param b: a 3-tuple of the nominal value, plus, and minus tolerances for a second StackDim.
        :returns: A 2-tuple containing the plus and minus tolerances of the result of worst-case taking a^b.
    """
    nom = a[0] ** b[0]
    a_vals = np.array([a[1], a[2]])
    b_vals = np.array([b[1], b[2]])

    # Create all 4 combinations of quotients
    powers = np.array([(a[0] + da) ** (b[0] + db) for da in a_vals for db in b_vals])

    deviations = powers - nom
    return max(deviations), min(deviations)


def sinBounds(dim: tuple[float, float, float]) -> tuple[float, float]:
    """
    Utility function to compute min/max of the sine of a toleranced value.

    The initial assumption is that the max is the higher of the two values computed from the
    tolerance limits, and the min is the lower.
    For the sine function, the max may accur at an interior point if for some k pi*(1/2+2*k) is within the range.
    In this case, the maximum is 1.
    Similarly for the min, it is -1 if for some k pi*(-1/2 + k) is within the range.

        :param dim: a 3-tuple of the nominal value, plus, and minus tolerances for a StackDim.
        :returns: A 2-tuple containing the plus and minus tolerances of the result of worst-case taking sin(dim).
    """

    _upper = dim[0] + dim[1]
    _lower = dim[0] + dim[2]
    _pi_by_2 = np.pi / 2

    _min = (
        -1
        if contains_angle(_lower, _upper, -_pi_by_2)
        else np.min(np.sin([_lower, _upper]))
    )
    _max = (
        1
        if contains_angle(_lower, _upper, _pi_by_2)
        else np.max(np.sin([_lower, _upper]))
    )

    nom = np.sin(dim[0])

    return (_max - nom, _min - nom)


def cosBounds(dim: tuple[float, float, float]) -> tuple[float, float]:
    """
    Utility function to compute min/max of the cosine of a toleranced value.

    The initial assumption is that the max is the higher of the two values computed from the
    tolerance limits, and the min is the lower.
    For the cosine function, the max may accur at an interior point if for some k 2*pi*k is within the range.
    In this case, the maximum is 1.
    Similarly for the min, it is -1 if for some k pi*(1 + 2*k) is within the range.

        :param dim: a 3-tuple of the nominal value, plus, and minus tolerances for a StackDim.
        :returns: A 2-tuple containing the plus and minus tolerances of the result of worst-case taking cos(dim).
    """
    _upper = dim[0] + dim[1]
    _lower = dim[0] + dim[2]

    _min = (
        -1
        if contains_angle(_lower, _upper, np.pi)
        else np.min(np.cos([_lower, _upper]))
    )
    _max = 1 if contains_angle(_lower, _upper, 0) else np.max(np.cos([_lower, _upper]))

    nom = np.cos(dim[0])

    return (_max - nom, _min - nom)


def tanBounds(dim: tuple[float, float, float]) -> tuple[float, float]:
    """
    Utility function to compute min/max of the tangent of a toleranced value.

    The initial assumption is that the max is the higher of the two values computed from the
    tolerance limits, and the min is the lower.
    For the tangent function, both extrema blow up if pi/2 or -pi/2 are in the range. In this
    case, throws a ValueError indicating the issue.

        :param dim: a 3-tuple of the nominal value, plus, and minus tolerances for a StackDim.
        :returns: A 2-tuple containing the plus and minus tolerances of the result of worst-case taking tan(dim).
    """
    _upper = dim[0] + dim[1]
    _lower = dim[0] + dim[2]

    if contains_angle(_lower, _upper, np.pi / 2) or contains_angle(
        _lower, _upper, -np.pi / 2
    ):
        raise ValueError(
            f"Cannot compute tangent bounds for input {dim}, range contains a discontinuity in the tangent function."
        )

    _min = np.min(np.tan([_lower, _upper]))
    _max = np.max(np.tan([_lower, _upper]))
    nom = np.tan(dim[0])

    return (_max - nom, _min - nom)


def contains_angle(lower, upper, theta):
    """
    Checks if the angle theta exists in the closed interval from the lower to upper bound, mod 2*pi

    This is true when lower < theta + 2*pi*k < upper.
    Refactoring, we have (lower-theta)/(2*pi) < k < (upper-theta)/(2*pi)
    Therefore if ceil of the left hand side is less than or equal to floor of the right hand side, theta is within the range

    Parameters:
    lower (int or float): The lower bound parameter in radians.
    upper (int or float): The upper bound parameter in radians.
    theta (int or float): The angle parameter in radians.

    Returns:
    bool: True if theta is within the range mod 2*pi, False otherwise.
    """

    left = (lower - theta) / (2 * np.pi)
    right = (upper - theta) / (2 * np.pi)

    right_eval = np.floor(right)
    left_eval = np.ceil(left)

    return right_eval - left_eval > 0 or isclose(right_eval, left_eval, abs_tol=1e-9)
