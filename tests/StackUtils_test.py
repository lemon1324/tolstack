import unittest

from tolstack.StackUtils import *


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
        self.assertFalse(is_operator("a"))
        self.assertFalse(is_operator("1"))

    def test_is_variable(self):
        self.assertTrue(is_variable("D1"))
        self.assertTrue(is_variable("E13"))
        self.assertTrue(is_variable("LONG_NAME_EXPRESSION"))
        self.assertFalse(is_variable("+="))
        self.assertFalse(is_variable("*"))

    def test_get_precedence(self):
        self.assertEqual(get_precedence("+"), 1)
        self.assertEqual(get_precedence("*"), 2)
        self.assertEqual(get_precedence("^"), 3)
        with self.assertRaises(KeyError):
            get_precedence("(")

    def test_parse_string_to_numeric(self):
        self.assertEqual(parse_string_to_numeric("123.45"), 123.45)
        self.assertEqual(parse_string_to_numeric("0"), 0.0)
        self.assertIsNone(parse_string_to_numeric("abc"))
        self.assertIsNone(parse_string_to_numeric("12a"))


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
