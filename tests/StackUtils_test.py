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
