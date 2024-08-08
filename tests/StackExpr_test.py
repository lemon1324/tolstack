import unittest
import numpy as np

from tolstack.StackParser import StackParser
from tolstack.gui.FileIO import open_from_name
from tolstack.gui.GUITypes import DataWidget


class TestStackExprDerivatives(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        # D1 = 2
        # D2 = 3
        # D3 = 5
        # D4 = 0.785 (approx pi/4 = 45deg)
        # D5 = 30
        self.SP = StackParser()

        info = open_from_name("validation_inputs/test_expression_derivative.txt")
        self.SP.parse(
            constants_data=info[DataWidget.CONSTANTS],
            dimensions_data=info[DataWidget.DIMENSIONS],
            expressions_data=info[DataWidget.EXPRESSIONS],
        )

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

    def test_simpleSin(self):
        # E9 = 'sin D4'
        expr = self.SP.expressions["E9"]
        nominal_val = np.sin(0.785)

        # Derivative w.r.t. D4, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D4")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(partial, np.cos(0.785))

        # Derivative w.r.t. D1, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(partial, 0)

    def test_simpleCos(self):
        # E10 = 'cos D4'
        expr = self.SP.expressions["E10"]
        nominal_val = np.cos(0.785)

        # Derivative w.r.t. D4, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D4")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(partial, -np.sin(0.785))

        # Derivative w.r.t. D1, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(partial, 0)

    def test_simpleTan(self):
        # E11 = 'tan D4'
        expr = self.SP.expressions["E11"]
        nominal_val = np.tan(0.785)

        # Derivative w.r.t. D4, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D4")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(partial, (1 / np.cos(0.785)) ** 2)

        # Derivative w.r.t. D1, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(partial, 0)

    def test_simpleSinDegrees(self):
        # E12 = 'sind D5'
        expr = self.SP.expressions["E12"]
        nominal_val = np.sin(np.radians(30))

        # Derivative w.r.t. D5, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D5")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(partial, np.cos(np.radians(30)) * np.radians(1))

        # Derivative w.r.t. D1, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(partial, 0)

    def test_simpleCosDegrees(self):
        # E13 = 'cosd D5'
        expr = self.SP.expressions["E13"]
        nominal_val = np.cos(np.radians(30))

        # Derivative w.r.t. D5, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D5")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(partial, -np.sin(np.radians(30)) * np.radians(1))

        # Derivative w.r.t. D1, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(partial, 0)

    def test_simpleTanDegrees(self):
        # E14 = 'tand D5'
        expr = self.SP.expressions["E14"]
        nominal_val = np.tan(np.radians(30))

        # Derivative w.r.t. D5, which is present
        nom, partial = expr._evaluateDerivative(expr.root, "D5")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(
            partial, (1 / np.cos(np.radians(30)) ** 2) * np.radians(1)
        )

        # Derivative w.r.t. D1, which is absent
        nom, partial = expr._evaluateDerivative(expr.root, "D1")
        self.assertAlmostEqual(nom, nominal_val)
        self.assertAlmostEqual(partial, 0)


class TestStackExprExpand(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        # D1 = 2
        # D2 = 3
        # D3 = 5
        self.SP = StackParser()

        info = open_from_name("validation_inputs/test_expression_expand.txt")
        self.SP.parse(
            constants_data=info[DataWidget.CONSTANTS],
            dimensions_data=info[DataWidget.DIMENSIONS],
            expressions_data=info[DataWidget.EXPRESSIONS],
        )

        self.value_map = self.SP.constants | self.SP.dimensions

    def test_singleDimension(self):
        # E1 = 'D1'
        expr = self.SP.expressions["E1"]

        expanded = expr.expand()
        self.assertEqual(expanded, "D1")

    def test_sum(self):
        # E2 = 'D1 + 5'
        expr = self.SP.expressions["E2"]

        expanded = expr.expand()
        self.assertEqual(expanded, "D1 + 5")

    def test_difference(self):
        # E3 = 'D1 - D2'
        expr = self.SP.expressions["E3"]

        expanded = expr.expand()
        self.assertEqual(expanded, "D1 - D2")

    def test_productExpansion(self):
        # E4 = 'D2*E2' = 'D2*(D1+5)'
        expr = self.SP.expressions["E4"]

        expanded = expr.expand()
        self.assertEqual(expanded, "D2 * (D1 + 5)")

    def test_subtractionOnRight(self):
        # E5 = 'D3-E3' = 'D3-(D1-D2)'
        expr = self.SP.expressions["E5"]

        expanded = expr.expand()
        self.assertEqual(expanded, "D3 - (D1 - D2)")

    def test_multipleSubtractions(self):
        # E6 = 'D3-D2-D1'
        expr = self.SP.expressions["E6"]

        expanded = expr.expand()
        self.assertEqual(expanded, "D3 - D2 - D1")

    def test_compositeExpression(self):
        # E10 = '(3*D1+2*D2)/D3'
        expr = self.SP.expressions["E10"]

        expanded = expr.expand()
        self.assertEqual(expanded, "(3 * D1 + 2 * D2) / D3")
