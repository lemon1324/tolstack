import unittest

from tests.TestUtils import addCombination
from tests.TestUtils import subtractCombination


class TestTestUtils(unittest.TestCase):
    def test_addCombinationPlusMinus(self) -> None:
        a = (0.2, -0.1)
        b = (0.8, -0.5)
        plus, minus = addCombination(a, b)
        self.assertAlmostEqual(
            plus, 1.0, msg="Incorrect plus tolerance for plus/minus input"
        )
        self.assertAlmostEqual(
            minus, -0.6, msg="Incorrect minus tolerance for plus/minus input"
        )

    def test_addCombinationPlusPlus(self) -> None:
        a = (0.2, 0.1)
        b = (0.8, 0.5)
        plus, minus = addCombination(a, b)
        self.assertAlmostEqual(
            plus, 1.0, msg="Incorrect plus tolerance for plus/plus input"
        )
        self.assertAlmostEqual(
            minus, 0.6, msg="Incorrect minus tolerance for plus/plus input"
        )

    def test_addCombinationMinusMinus(self) -> None:
        a = (-0.1, -0.2)
        b = (-0.5, -0.8)
        plus, minus = addCombination(a, b)
        self.assertAlmostEqual(
            plus, -0.6, msg="Incorrect plus tolerance for minus/minus input"
        )
        self.assertAlmostEqual(
            minus, -1.0, msg="Incorrect minus tolerance for minus/minus input"
        )

    def test_subtractCombinationPlusMinus(self) -> None:
        a = (0.2, -0.1)
        b = (0.8, -0.5)
        plus, minus = subtractCombination(a, b)
        self.assertAlmostEqual(
            plus, 0.7, msg="Incorrect plus tolerance for plus/minus input"
        )
        self.assertAlmostEqual(
            minus, -0.9, msg="Incorrect minus tolerance for plus/minus input"
        )

    def test_subtractCombinationPlusPlus(self) -> None:
        a = (0.2, 0.1)
        b = (0.8, 0.5)
        plus, minus = subtractCombination(a, b)
        self.assertAlmostEqual(
            plus, -0.3, msg="Incorrect plus tolerance for plus/plus input"
        )
        self.assertAlmostEqual(
            minus, -0.7, msg="Incorrect minus tolerance for plus/plus input"
        )

    def test_subtractCombinationMinusMinus(self) -> None:
        a = (-0.1, -0.2)
        b = (-0.5, -0.8)
        plus, minus = subtractCombination(a, b)
        self.assertAlmostEqual(
            plus, 0.7, msg="Incorrect plus tolerance for minus/minus input"
        )
        self.assertAlmostEqual(
            minus, 0.3, msg="Incorrect minus tolerance for minus/minus input"
        )
