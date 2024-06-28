import unittest

from tolstack.StackExpr import StackExpr
from tolstack.StackParser import StackParser


class TestStackExprDerivatives(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        # D1 = 2
        # D2 = 3
        # D3 = 5
        self.SP = StackParser()

        with open("validation_inputs/test_Expression_derivative.txt", "r") as file:
            lines = file.readlines()

        self.SP.parse(lines)

        self.value_map = self.SP.constants | self.SP.dimensions

    def test_singleDimension(self):
        # E1 = 'D1'
        expr = self.SP.expressions["E1"]

        # Derivative w.r.t. D1, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, 2)
        self.assertAlmostEqual(partial, 1)

        # Derivative w.r.t. D2, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D2")
        self.assertAlmostEqual(nom, 2)
        self.assertAlmostEqual(partial, 0)

    def test_scalarAddition(self):
        # E2 = 'D1 + 5'
        expr = self.SP.expressions["E2"]

        # Derivative w.r.t. D1, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, 7)
        self.assertAlmostEqual(partial, 1)

        # Derivative w.r.t. D2, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D2")
        self.assertAlmostEqual(nom, 7)
        self.assertAlmostEqual(partial, 0)

    def test_scalarProduct(self):
        # E3 = 'D1*7'
        expr = self.SP.expressions["E3"]

        # Derivative w.r.t. D1, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, 14)
        self.assertAlmostEqual(partial, 7)

        # Derivative w.r.t. D2, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D2")
        self.assertAlmostEqual(nom, 14)
        self.assertAlmostEqual(partial, 0)

    def test_dimensionProduct(self):
        # E4 = 'D2*D3'
        expr = self.SP.expressions["E4"]

        # Derivative w.r.t. D2, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D2")
        self.assertAlmostEqual(nom, 15)
        self.assertAlmostEqual(partial, 5)

        # Derivative w.r.t. D3, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D3")
        self.assertAlmostEqual(nom, 15)
        self.assertAlmostEqual(partial, 3)

        # Derivative w.r.t. D1, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, 15)
        self.assertAlmostEqual(partial, 0)

    def test_scalarDivisor(self):
        # E5 = 'D3/5'
        expr = self.SP.expressions["E5"]

        # Derivative w.r.t. D3, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D3")
        self.assertAlmostEqual(nom, 1)
        self.assertAlmostEqual(partial, 1 / 5)

        # Derivative w.r.t. D1, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, 1)
        self.assertAlmostEqual(partial, 0)

    def test_scalarDividend(self):
        # E6 = '3/D2'
        expr = self.SP.expressions["E6"]

        # Derivative w.r.t. D2, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D2")
        self.assertAlmostEqual(nom, 1)
        self.assertAlmostEqual(partial, -1 / 3)

        # Derivative w.r.t. D1, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, 1)
        self.assertAlmostEqual(partial, 0)

    def test_dimensionDivision(self):
        # E7 = 'D1/D3'
        expr = self.SP.expressions["E7"]

        # Derivative w.r.t. D1, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, 2 / 5)
        self.assertAlmostEqual(partial, 1 / 5)

        # Derivative w.r.t. D2, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D2")
        self.assertAlmostEqual(nom, 2 / 5)
        self.assertAlmostEqual(partial, 0)

        # Derivative w.r.t. D3, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D3")
        self.assertAlmostEqual(nom, 2 / 5)
        self.assertAlmostEqual(partial, -2 / 25)

    def test_dimensionComposite(self):
        # E8 = '(3*D1+2*D2)/D3'
        expr = self.SP.expressions["E8"]

        # Derivative w.r.t. D1, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, 12 / 5)
        self.assertAlmostEqual(partial, 3 / 5)

        # Derivative w.r.t. D2, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D2")
        self.assertAlmostEqual(nom, 12 / 5)
        self.assertAlmostEqual(partial, 2 / 5)

        # Derivative w.r.t. D3, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D3")
        self.assertAlmostEqual(nom, 12 / 5)
        self.assertAlmostEqual(partial, -12 / 25)

        # Derivative w.r.t. D4, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D4")
        self.assertAlmostEqual(nom, 12 / 5)
        self.assertAlmostEqual(partial, 0)
