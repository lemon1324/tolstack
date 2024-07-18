import unittest

from tolstack.StackFormat import (
    format_shortest,
    format_scientific,
    format_significant_figures,
    round_string,
)


class TestFormatShortest(unittest.TestCase):

    def test_format_shortest_scientific(self):
        # Test case where scientific notation is shorter
        num = 0.000012345
        sig_figs = 3
        result = format_shortest(num, sig_figs)
        expected = "+1.23e-5"
        self.assertEqual(result, expected)

    def test_format_shortest_decimal(self):
        # Test case where decimal notation is shorter
        num = 12345
        sig_figs = 4
        result = format_shortest(num, sig_figs)
        expected = "+12350"  # Example based on significant figures
        self.assertEqual(result, expected)

    def test_format_shortest_with_leading_zeroes(self):
        # Test case with leading zeroes
        num = 0.0054314
        sig_figs = 4
        leading_zeroes = True
        result = format_shortest(num, sig_figs, leading_zeroes)
        expected = "+0.005431"  # Example based on significant figures with rounding
        self.assertEqual(result, expected)

    def test_format_shortest_no_leading_zeroes(self):
        # Test case without leading zeroes
        num = 0.0012345
        sig_figs = 2
        leading_zeroes = False
        result = format_shortest(num, sig_figs, leading_zeroes)
        expected = "+.0012"
        self.assertEqual(result, expected)

    def test_format_shortest_negative_number(self):
        # Test case with negative number
        num = -0.000012345
        sig_figs = 3
        result = format_shortest(num, sig_figs)
        expected = "-1.23e-5"
        self.assertEqual(result, expected)

    def test_format_shortest_large_number(self):
        # Test case with large number
        num = 123456789
        sig_figs = 4
        result = format_shortest(num, sig_figs)
        expected = "+1.235e+8"  # Example based on significant figures with rounding
        self.assertEqual(result, expected)


class TestFormatScientific(unittest.TestCase):

    def test_default_precision_and_exp_digits(self):
        self.assertEqual(format_scientific(12345.6789), "+1.2346e+04")

    def test_custom_precision(self):
        self.assertEqual(format_scientific(12345.6789, precision=2), "+1.23e+04")

    def test_custom_exp_digits(self):
        self.assertEqual(format_scientific(12345.6789, exp_digits=3), "+1.2346e+004")

    def test_negative_number(self):
        self.assertEqual(
            format_scientific(-12345.6789, precision=3, exp_digits=3), "-1.235e+004"
        )

    def test_large_exponent(self):
        self.assertEqual(
            format_scientific(1.23e100, precision=2, exp_digits=4), "+1.23e+0100"
        )

    def test_small_exponent(self):
        self.assertEqual(
            format_scientific(1.23e-10, precision=2, exp_digits=4), "+1.23e-0010"
        )


class TestFormatSignificantFigures(unittest.TestCase):

    def test_default_behavior(self):
        self.assertEqual(format_significant_figures(12345.6789, 5), "+12346.")

    def test_leading_zeros_false(self):
        self.assertEqual(format_significant_figures(0.00123456789, 2), "+.0012")

    def test_leading_zeros_true(self):
        self.assertEqual(
            format_significant_figures(0.00123456789, 2, leading_zeros=True), "+0.0012"
        )

    def test_integer_part_truncation(self):
        self.assertEqual(format_significant_figures(123456789, 5), "+123460000")

    def test_fractional_part(self):
        self.assertEqual(format_significant_figures(0.000123456789, 5), "+.00012345")

    # because this has a terminating binary representation, the initial string
    # may end up shorter than the desired precision (as it does in this case)
    def test_inv_power_2(self):
        self.assertEqual(format_significant_figures(0.125, 4), "+.1250")

    def test_nonzero_integer_with_fraction(self):
        self.assertEqual(format_significant_figures(12345.6789, 7), "+12345.68")

    def test_zero(self):
        self.assertEqual(format_significant_figures(0, 5), "+.00000")


class TestRoundString(unittest.TestCase):
    def test_less_than_digits(self):
        self.assertEqual(round_string("123", 5), "123")

    def test_equal_to_digits(self):
        self.assertEqual(round_string("12345", 5), "12345")

    def test_round_up_middle_digit(self):
        self.assertEqual(round_string("123456", 5), "12346")

    def test_round_up_last_digit(self):
        self.assertEqual(round_string("123459", 5), "12346")

    def test_round_up_with_nine_at_cutoff(self):
        self.assertEqual(round_string("123495", 5), "12350")

    def test_round_up_multiple_nines(self):
        self.assertEqual(round_string("129999", 5), "13000")

    def test_round_up_all_nines(self):
        self.assertEqual(round_string("99999", 4), "10000")

    def test_no_rounding_needed(self):
        self.assertEqual(round_string("123454", 5), "12345")

    def test_no_rounding_high_digit_no_change(self):
        self.assertEqual(round_string("123494", 5), "12349")
