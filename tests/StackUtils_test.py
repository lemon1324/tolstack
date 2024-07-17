import unittest

from tolstack.StackUtils import *

import numpy as np


class TestExpressionFunctions(unittest.TestCase):

    def test_tokenize(self):
        self.assertEqual(tokenize("a + b - c"), ["a", "+", "b", "-", "c"])
        self.assertEqual(
            tokenize("3 * (4 + 5) / 6"), ["3", "*", "(", "4", "+", "5", ")", "/", "6"]
        )
        self.assertEqual(
            tokenize("x^2 + y^2 + z^2"),
            ["x", "^", "2", "+", "y", "^", "2", "+", "z", "^", "2"],
        )

    def test_is_operator(self):
        self.assertTrue(is_operator("+"))
        self.assertTrue(is_operator("-"))
        self.assertTrue(is_operator("sin"))
        self.assertFalse(is_operator("a"))
        self.assertFalse(is_operator("1"))
        self.assertFalse(
            is_operator("u-")
        )  # unary operator encoding is not an operator for infix expressions

    def test_can_be_unary_operator_with_minus(self):
        token = "-"
        self.assertTrue(can_be_unary_operator(token))

    def test_can_be_unary_operator_with_sin(self):
        token = "sin"
        self.assertTrue(can_be_unary_operator(token))

    def test_can_be_unary_operator_with_invalid(self):
        token = "+"
        self.assertFalse(can_be_unary_operator(token))

    def test_is_unary_operator_with_u_minus(self):
        token = "u-"
        self.assertTrue(is_unary_operator(token))

    def test_is_unary_operator_with_sine(self):
        token = "sin"
        self.assertTrue(is_unary_operator(token))

    def test_is_unary_operator_with_invalid(self):
        token = "+"
        self.assertFalse(is_unary_operator(token))

    def test_is_variable(self):
        self.assertTrue(is_variable("D1"))
        self.assertTrue(is_variable("E13"))
        self.assertTrue(is_variable("LONG_NAME_EXPRESSION"))
        self.assertFalse(is_variable("+="))
        self.assertFalse(is_variable("sin"))
        self.assertFalse(is_variable("*"))
        self.assertFalse(
            is_variable("u-")
        )  # unary operator encoding is not a variable in RPN expressions

    def test_get_precedence(self):
        self.assertEqual(get_precedence("+"), 1)
        self.assertEqual(get_precedence("*"), 2)
        self.assertEqual(get_precedence("^"), 3)
        with self.assertRaises(KeyError):
            get_precedence("(")


class TestIsNumericString(unittest.TestCase):

    def test_valid_numeric_strings(self):
        self.assertTrue(is_numeric_string("123"))
        self.assertTrue(is_numeric_string("123.45"))
        self.assertTrue(is_numeric_string("-123.45"))
        self.assertTrue(is_numeric_string("1e3"))
        self.assertTrue(is_numeric_string("0.0"))
        self.assertTrue(is_numeric_string("0"))

    def test_invalid_numeric_strings(self):
        self.assertFalse(is_numeric_string("abc"))
        self.assertFalse(is_numeric_string("123abc"))
        self.assertFalse(is_numeric_string(""))
        self.assertFalse(is_numeric_string(None))

    def test_nan_string(self):
        self.assertFalse(is_numeric_string("nan"))
        self.assertFalse(is_numeric_string("NaN"))

    def test_inf_string(self):
        self.assertTrue(is_numeric_string("inf"))
        self.assertTrue(is_numeric_string("-inf"))
        self.assertTrue(is_numeric_string("Infinity"))
        self.assertTrue(is_numeric_string("-Infinity"))


class TestParseStringToNumeric(unittest.TestCase):

    def test_valid_numbers(self):
        self.assertAlmostEqual(parse_string_to_numeric("123"), 123.0)
        self.assertAlmostEqual(parse_string_to_numeric("123.45"), 123.45)
        self.assertAlmostEqual(parse_string_to_numeric("-123"), -123.0)
        self.assertAlmostEqual(parse_string_to_numeric("-123.45"), -123.45)
        self.assertAlmostEqual(parse_string_to_numeric("0"), 0.0)
        self.assertAlmostEqual(
            parse_string_to_numeric("1e3"), 1000.0
        )  # scientific notation

    def test_invalid_numbers(self):
        self.assertIsNone(parse_string_to_numeric("abc"))
        self.assertIsNone(parse_string_to_numeric("123abc"))
        self.assertIsNone(parse_string_to_numeric(""))
        self.assertIsNone(parse_string_to_numeric(" "))
        self.assertIsNone(parse_string_to_numeric(None))
        self.assertIsNone(parse_string_to_numeric("NaN"))  # Not a Number

    def test_edge_cases(self):
        self.assertAlmostEqual(parse_string_to_numeric("inf"), float("inf"))
        self.assertAlmostEqual(parse_string_to_numeric("-inf"), float("-inf"))
        self.assertAlmostEqual(parse_string_to_numeric("+inf"), float("inf"))
        self.assertAlmostEqual(parse_string_to_numeric(".5"), 0.5)
        self.assertAlmostEqual(parse_string_to_numeric("-.5"), -0.5)


class TestPercentToFraction(unittest.TestCase):

    def test_valid_percentages(self):
        self.assertAlmostEqual(percent_to_fraction("75%"), 0.75)
        self.assertAlmostEqual(percent_to_fraction("12.5%"), 0.125)
        self.assertAlmostEqual(percent_to_fraction("12.%"), 0.12)
        self.assertAlmostEqual(percent_to_fraction("100%"), 1.0)
        self.assertAlmostEqual(percent_to_fraction("0%"), 0.0)
        self.assertAlmostEqual(percent_to_fraction("99.9%"), 0.999)
        self.assertAlmostEqual(percent_to_fraction("-50%"), -0.5)
        self.assertAlmostEqual(percent_to_fraction("50 %"), 0.5)

    def test_invalid_percentages(self):
        self.assertIsNone(percent_to_fraction("invalid%"))
        self.assertIsNone(percent_to_fraction("123"))
        self.assertIsNone(percent_to_fraction("%"))
        self.assertIsNone(percent_to_fraction("12.5%%"))

    def test_edge_cases(self):
        self.assertIsNone(percent_to_fraction(""))
        self.assertIsNone(percent_to_fraction(" "))
        self.assertIsNone(percent_to_fraction(None))
        self.assertIsNone(percent_to_fraction("%%"))


class TestInfixToRPN(unittest.TestCase):

    def test_simple_addition(self):
        expression = "3 + 4"
        expected_output = ["3", "4", "+"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_precedence(self):
        expression = "3 + 4 * 2"
        expected_output = ["3", "4", "2", "*", "+"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_parentheses(self):
        expression = "( 3 + 4 ) * 2"
        expected_output = ["3", "4", "+", "2", "*"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_complex_expression(self):
        expression = "3 + 4 * ( 2 - 1 ) / 5 ^ 2"
        expected_output = ['3', '4', '2', '1', '-', '*', '5', '2', '^', '/', '+']
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_complex_expression_2(self):
        expression = "(D2/D3) - (D3/(D1+D2))"
        expected_output = ["D2", "D3", "/", "D3", "D1", "D2", "+", "/", "-"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_series_subtraction(self):
        expression = "x - y - z"
        expected_output = ["x", "y", "-", "z", "-"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_nested_parentheses(self):
        expression = "3 + ( 4 * ( 2 - 1 ) )"
        expected_output = ["3", "4", "2", "1", "-", "*", "+"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_unary_minus_simple(self):
        expression = "-3"
        expected_output = ["3", "u-"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_unary_minus_within_expression(self):
        expression = "3 * -4"
        expected_output = ["3", "4", "u-", "*"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_unary_minus_with_parentheses(self):
        expression = "3 * ( -4 + 2 )"
        expected_output = ["3", "4", "u-", "2", "+", "*"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_unary_minus_outside_parentheses(self):
        expression = "3 * -( 4 + 2 )"
        expected_output = ["3", "4", "2", "+", "u-", "*"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_double_unary_minus(self):
        expression = "--x"
        expected_output = ["x", "u-", "u-"]
        self.assertEqual(infix_to_rpn(expression), expected_output)


class TestTrigInfixToRPN(unittest.TestCase):
    def test_simple_sine(self):
        expression = "sin x"
        expected_output = ["x", "sin"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_simple_cosine(self):
        expression = "cos x"
        expected_output = ["x", "cos"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_simple_tangent(self):
        expression = "tan x"
        expected_output = ["x", "tan"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_simple_sine_parens(self):
        expression = "sin(x)"
        expected_output = ["x", "sin"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_simple_sine_negation_inside(self):
        expression = "sin -x"
        expected_output = ["x", "u-", "sin"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_simple_sine_negation_outside(self):
        expression = "-sin x"
        expected_output = ["x", "sin", "u-"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_sine_addition(self):
        expression = "sin x + y"
        expected_output = ["x", "sin", "y", "+"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_sine_multiplication(self):
        expression = "sin x * y"
        expected_output = ["x", "sin", "y", "*"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_sine_with_parentheses(self):
        expression = "sin (x + y)"
        expected_output = ["x", "y", "+", "sin"]
        self.assertEqual(infix_to_rpn(expression), expected_output)

    def test_complex_expression(self):
        expression = "sin x + cos y * tan z"
        expected_output = ["x", "sin", "y", "cos", "z", "tan", "*", "+"]
        self.assertEqual(infix_to_rpn(expression), expected_output)


class TestAddCombination(unittest.TestCase):
    def test_addCombinationPlusMinus(self) -> None:
        a = (0.2, -0.1)
        b = (0.8, -0.5)
        plus, minus = addCombination(a, b)
        self.assertAlmostEqual(plus, 1.0)
        self.assertAlmostEqual(minus, -0.6)

    def test_addCombinationPlusPlus(self) -> None:
        a = (0.2, 0.1)
        b = (0.8, 0.5)
        plus, minus = addCombination(a, b)
        self.assertAlmostEqual(plus, 1.0)
        self.assertAlmostEqual(minus, 0.6)

    def test_addCombinationMinusMinus(self) -> None:
        a = (-0.1, -0.2)
        b = (-0.5, -0.8)
        plus, minus = addCombination(a, b)
        self.assertAlmostEqual(plus, -0.6)
        self.assertAlmostEqual(minus, -1.0)


class TestSubtractCombination(unittest.TestCase):
    def test_subtractCombinationPlusMinus(self) -> None:
        a = (0.2, -0.1)
        b = (0.8, -0.5)
        plus, minus = subtractCombination(a, b)
        self.assertAlmostEqual(plus, 0.7)
        self.assertAlmostEqual(minus, -0.9)

    def test_subtractCombinationPlusPlus(self) -> None:
        a = (0.2, 0.1)
        b = (0.8, 0.5)
        plus, minus = subtractCombination(a, b)
        self.assertAlmostEqual(plus, -0.3)
        self.assertAlmostEqual(minus, -0.7)

    def test_subtractCombinationMinusMinus(self) -> None:
        a = (-0.1, -0.2)
        b = (-0.5, -0.8)
        plus, minus = subtractCombination(a, b)
        self.assertAlmostEqual(plus, 0.7)
        self.assertAlmostEqual(minus, 0.3)


class TestMulCombination(unittest.TestCase):
    def test_mulCombinationPlusMinus(self) -> None:
        a = (2, 0.2, -0.1)
        b = (3, 0.8, -0.5)
        plus, minus = mulCombination(a, b)
        self.assertAlmostEqual(plus, 2.36)
        self.assertAlmostEqual(minus, -1.25)

    def test_mulCombinationPlusPlus(self) -> None:
        a = (2, 0.2, 0.1)
        b = (3, 0.8, 0.5)
        plus, minus = mulCombination(a, b)
        self.assertAlmostEqual(plus, 2.36)
        self.assertAlmostEqual(minus, 1.35)

    def test_mulCombinationMinusMinus(self) -> None:
        a = (2, -0.1, -0.2)
        b = (3, -0.5, -0.8)
        plus, minus = mulCombination(a, b)
        self.assertAlmostEqual(plus, -1.25)
        self.assertAlmostEqual(minus, -2.04)


class TestDivCombination(unittest.TestCase):
    def test_divCombinationPlusMinus(self) -> None:
        a = (2, 0.2, -0.1)
        b = (3, 0.8, -0.5)
        plus, minus = divCombination(a, b)
        self.assertAlmostEqual(plus, 0.21333333)
        self.assertAlmostEqual(minus, -0.16666666)

    def test_divCombinationPlusPlus(self) -> None:
        a = (2, 0.2, 0.1)
        b = (3, 0.8, 0.5)
        plus, minus = divCombination(a, b)
        self.assertAlmostEqual(plus, -0.038095238)
        self.assertAlmostEqual(minus, -0.114035088)

    def test_divCombinationMinusMinus(self) -> None:
        a = (2, -0.1, -0.2)
        b = (3, -0.5, -0.8)
        plus, minus = divCombination(a, b)
        self.assertAlmostEqual(plus, 0.196969697)
        self.assertAlmostEqual(minus, 0.053333333)


class TestExpCombination(unittest.TestCase):
    def test_expCombinationPlusMinus(self) -> None:
        a = (4, 0.2, -0.1)
        b = (2, 0.8, -0.5)
        plus, minus = expCombination(a, b)
        self.assertAlmostEqual(plus, 39.60297298665972)
        self.assertAlmostEqual(minus, -8.298117113328715)

    def test_expCombinationPlusPlus(self) -> None:
        a = (4, 0.2, 0.1)
        b = (2, 0.8, 0.5)
        plus, minus = expCombination(a, b)
        self.assertAlmostEqual(plus, 39.60297298665972)
        self.assertAlmostEqual(minus, 18.037655765343175)

    def test_expCombinationMinusMinus(self) -> None:
        a = (4, -0.1, -0.2)
        b = (2, -0.5, -0.8)
        plus, minus = expCombination(a, b)
        self.assertAlmostEqual(plus, -8.298117113328715)
        self.assertAlmostEqual(minus, -11.037045245114758)

    def test_expCombinationLessThanOne(self) -> None:
        a = (4, 0.3, -0.4)
        b = (0.5, 0.1, -0.2)
        plus, minus = expCombination(a, b)
        self.assertAlmostEqual(plus, 0.399280770828355)
        self.assertAlmostEqual(minus, -0.5314431944106439)


class TestContainsAngle(unittest.TestCase):

    def test_angle_within_range(self):
        self.assertTrue(contains_angle(0, np.pi, np.pi / 2))

    def test_angle_outside_range(self):
        self.assertFalse(contains_angle(0, np.pi / 2, np.pi))

    def test_angle_equal_lower_bound(self):
        self.assertTrue(contains_angle(np.pi / 2, np.pi, np.pi / 2))

    def test_angle_equal_upper_bound(self):
        self.assertTrue(contains_angle(0, np.pi / 2, np.pi / 2))

    def test_angle_outside_range_negative(self):
        self.assertFalse(contains_angle(-np.pi / 4, np.pi / 4, 3 * np.pi / 4))

    def test_angle_large_values(self):
        self.assertTrue(contains_angle(0, 10 * np.pi, 4.5 * np.pi))

    def test_angle_negative_theta(self):
        self.assertTrue(contains_angle(-np.pi, 0, -np.pi / 2))

    def test_angle_in_modulo_range(self):
        self.assertTrue(contains_angle(2 * np.pi, 3 * np.pi, np.pi / 2))


class TestSinBounds(unittest.TestCase):

    def test_low_range(self):
        (nom, plus, minus) = (np.pi / 4, np.pi / 8, -np.pi / 8)
        (upper, lower) = sinBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, np.sin(nom + minus) - np.sin(nom))
        self.assertAlmostEqual(upper, np.sin(nom + plus) - np.sin(nom))

    def test_high_range(self):
        (nom, plus, minus) = (3 * np.pi / 4, np.pi / 8, -np.pi / 8)
        (upper, lower) = sinBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, np.sin(nom + plus) - np.sin(nom))
        self.assertAlmostEqual(upper, np.sin(nom + minus) - np.sin(nom))

    def test_max_in_range(self):
        (nom, plus, minus) = (9 * np.pi / 16, np.pi / 8, -np.pi / 8)
        (upper, lower) = sinBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, np.sin(nom + plus) - np.sin(nom))
        self.assertAlmostEqual(upper, 1 - np.sin(nom))

    def test_max_in_modulo_range(self):
        (nom, plus, minus) = (41 * np.pi / 16, np.pi / 8, -np.pi / 8)
        (upper, lower) = sinBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, np.sin(nom + plus) - np.sin(nom))
        self.assertAlmostEqual(upper, 1 - np.sin(nom))

    def test_min_in_range(self):
        (nom, plus, minus) = (-9 * np.pi / 16, np.pi / 8, -np.pi / 8)
        (upper, lower) = sinBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, -1 - np.sin(nom))
        self.assertAlmostEqual(upper, np.sin(nom + minus) - np.sin(nom))

    def test_min_in_modulo_range(self):
        (nom, plus, minus) = (25 * np.pi / 16, np.pi / 8, -np.pi / 8)
        (upper, lower) = sinBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, -1 - np.sin(nom))
        self.assertAlmostEqual(upper, np.sin(nom + plus) - np.sin(nom))

    def test_both_in_range(self):
        (nom, plus, minus) = (0, 3 * np.pi / 2, -3 * np.pi / 2)
        (upper, lower) = sinBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, -1 - np.sin(nom))
        self.assertAlmostEqual(upper, 1 - np.sin(nom))


class TestCosBounds(unittest.TestCase):

    def test_low_range(self):
        (nom, plus, minus) = (-np.pi / 4, np.pi / 8, -np.pi / 8)
        (upper, lower) = cosBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, np.cos(nom + minus) - np.cos(nom))
        self.assertAlmostEqual(upper, np.cos(nom + plus) - np.cos(nom))

    def test_high_range(self):
        (nom, plus, minus) = (3 * np.pi / 4, np.pi / 8, -np.pi / 8)
        (upper, lower) = cosBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, np.cos(nom + plus) - np.cos(nom))
        self.assertAlmostEqual(upper, np.cos(nom + minus) - np.cos(nom))

    def test_max_in_range(self):
        (nom, plus, minus) = (0, np.pi / 8, -np.pi / 8)
        (upper, lower) = cosBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, np.cos(nom + plus) - np.cos(nom))
        self.assertAlmostEqual(upper, 1 - np.cos(nom))

    def test_max_in_modulo_range(self):
        (nom, plus, minus) = (2 * np.pi, np.pi / 8, -np.pi / 8)
        (upper, lower) = cosBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, np.cos(nom + plus) - np.cos(nom))
        self.assertAlmostEqual(upper, 1 - np.cos(nom))

    def test_min_in_range(self):
        (nom, plus, minus) = (np.pi, np.pi / 8, -np.pi / 8)
        (upper, lower) = cosBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, -1 - np.cos(nom))
        self.assertAlmostEqual(upper, np.cos(nom + minus) - np.cos(nom))

    def test_min_in_modulo_range(self):
        (nom, plus, minus) = (3 * np.pi, np.pi / 8, -np.pi / 8)
        (upper, lower) = cosBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, -1 - np.cos(nom))
        self.assertAlmostEqual(upper, np.cos(nom + minus) - np.cos(nom))

    def test_both_in_range(self):
        (nom, plus, minus) = (-np.pi / 4, 3 * np.pi / 2, -3 * np.pi / 2)
        (upper, lower) = cosBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, -1 - np.cos(nom))
        self.assertAlmostEqual(upper, 1 - np.cos(nom))


class TestTanBounds(unittest.TestCase):

    def test_low_range(self):
        (nom, plus, minus) = (np.pi / 4, np.pi / 8, -np.pi / 8)
        (upper, lower) = tanBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, np.tan(nom + minus) - np.tan(nom))
        self.assertAlmostEqual(upper, np.tan(nom + plus) - np.tan(nom))

    def test_high_range(self):
        (nom, plus, minus) = (3 * np.pi / 4, np.pi / 8, -np.pi / 8)
        (upper, lower) = tanBounds((nom, plus, minus))
        self.assertAlmostEqual(lower, np.tan(nom + minus) - np.tan(nom))
        self.assertAlmostEqual(upper, np.tan(nom + plus) - np.tan(nom))

    def test_discontinuity_in_range(self):
        with self.assertRaises(ValueError) as context:
            tanBounds((np.pi / 2, np.pi / 8, -np.pi / 8))

    def test_discontinuity_in_modulo_range(self):
        with self.assertRaises(ValueError) as context:
            tanBounds((3 * np.pi / 2, np.pi / 8, -np.pi / 8))
