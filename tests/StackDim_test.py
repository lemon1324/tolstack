import unittest

from tolstack.StackDim import StackDim
from tolstack.StackTypes import DistType

from tolstack.StackUtils import (
    addCombination,
    subtractCombination,
    mulCombination,
    divCombination,
)

import numpy as np

from tolstack.StackUtils import sinBounds, cosBounds, tanBounds


class TestStackDim(unittest.TestCase):
    def setUp(self) -> None:
        self.baseDim = StackDim(5.0, 0.1, -0.2)
        self.int = 4
        self.float = 5.3

    def test_init(self) -> None:
        self.assertEqual(
            self.baseDim.nom, 5.0, "Incorrect nominal value stored on creation."
        )
        self.assertEqual(
            self.baseDim.plus, 0.1, "Incorrect plus tolerance stored on creation."
        )
        self.assertEqual(
            self.baseDim.minus, -0.2, "Incorrect minus tolerance stored on creation."
        )
        self.assertEqual(
            self.baseDim.disttype,
            DistType.UNIFORM,
            "Incorrect distribution type stored on creation.",
        )

    def test_identity(self) -> None:
        self.cloneDim = StackDim(5.0, 0.1, -0.2)
        self.assertTrue(self.baseDim == self.cloneDim)


class TestAddNumeric(unittest.TestCase):
    def setUp(self) -> None:
        self.baseDim = StackDim(5.0, 0.1, -0.2)
        self.int = 4
        self.float = 5.3

    def test_addInt(self) -> None:
        outDim = self.baseDim + self.int
        self.assertEqual(
            outDim.nom,
            self.baseDim.nom + self.int,
            "Incorrect nominal value on integer addition.",
        )
        self.assertEqual(
            outDim.plus,
            self.baseDim.plus,
            "Incorrect plus tolerance on integer addition.",
        )
        self.assertEqual(
            outDim.minus,
            self.baseDim.minus,
            "Incorrect minus tolerance on integer addition.",
        )
        self.assertEqual(
            outDim.disttype,
            self.baseDim.disttype,
            "Incorrect distribution type on integer addition.",
        )
        self.assertIsNone(outDim.PN, "Incorrect PN for integer addition.")
        self.assertEqual(
            outDim.note, "Scalar shift.", "Incorrect note on integer addition."
        )

    def test_addRightInt(self) -> None:
        outDim = self.int + self.baseDim
        self.assertEqual(
            outDim.nom,
            self.baseDim.nom + self.int,
            "Incorrect nominal value on right integer addition.",
        )
        self.assertEqual(
            outDim.plus,
            self.baseDim.plus,
            "Incorrect plus tolerance on right integer addition.",
        )
        self.assertEqual(
            outDim.minus,
            self.baseDim.minus,
            "Incorrect minus tolerance on right integer addition.",
        )
        self.assertEqual(
            outDim.disttype,
            self.baseDim.disttype,
            "Incorrect distribution type on right integer addition.",
        )
        self.assertIsNone(outDim.PN, "Incorrect PN for right integer addition.")
        self.assertEqual(
            outDim.note, "Scalar shift.", "Incorrect note on right integer addition."
        )

    def test_intCommutativity(self) -> None:
        a = self.baseDim + self.int
        b = self.int + self.baseDim
        self.assertEqual(a, b, "Failed commutativity with integer addition.")

    def test_addFloat(self) -> None:
        outDim = self.baseDim + self.float
        self.assertEqual(
            outDim.nom,
            self.baseDim.nom + self.float,
            "Incorrect nominal value on float addition.",
        )
        self.assertEqual(
            outDim.plus,
            self.baseDim.plus,
            "Incorrect plus tolerance on float addition.",
        )
        self.assertEqual(
            outDim.minus,
            self.baseDim.minus,
            "Incorrect minus tolerance on float addition.",
        )
        self.assertEqual(
            outDim.disttype,
            self.baseDim.disttype,
            "Incorrect distribution type on float addition.",
        )
        self.assertIsNone(outDim.PN, "Incorrect PN for float addition.")
        self.assertEqual(
            outDim.note, "Scalar shift.", "Incorrect note on float addition."
        )

    def test_addRightFloat(self) -> None:
        outDim = self.float + self.baseDim
        self.assertEqual(
            outDim.nom,
            self.baseDim.nom + self.float,
            "Incorrect nominal value on right float addition.",
        )
        self.assertEqual(
            outDim.plus,
            self.baseDim.plus,
            "Incorrect plus tolerance on right float addition.",
        )
        self.assertEqual(
            outDim.minus,
            self.baseDim.minus,
            "Incorrect minus tolerance on right float addition.",
        )
        self.assertEqual(
            outDim.disttype,
            self.baseDim.disttype,
            "Incorrect distribution type on right float addition.",
        )
        self.assertIsNone(outDim.PN, "Incorrect PN for right float addition.")
        self.assertEqual(
            outDim.note, "Scalar shift.", "Incorrect note on right float addition."
        )

    def test_floatCommutativity(self) -> None:
        a = self.baseDim + self.float
        b = self.float + self.baseDim
        self.assertEqual(a, b, "Failed commutativity with float addition.")


class TestSubtractNumeric(unittest.TestCase):
    def setUp(self) -> None:
        self.baseDim = StackDim(5.0, 0.1, -0.2)
        self.int = 4
        self.float = 5.3

    def test_subtractInt(self) -> None:
        outDim = self.baseDim - self.int
        self.assertEqual(outDim.nom, self.baseDim.nom - self.int)
        self.assertEqual(outDim.plus, self.baseDim.plus)
        self.assertEqual(outDim.minus, self.baseDim.minus)
        self.assertEqual(outDim.disttype, self.baseDim.disttype)
        self.assertIsNone(outDim.PN)
        self.assertEqual(outDim.note, "Scalar shift.")

    def test_subtractRightInt(self) -> None:
        outDim = self.int - self.baseDim
        self.assertEqual(outDim.nom, self.int - self.baseDim.nom)
        self.assertEqual(outDim.plus, -self.baseDim.minus)
        self.assertEqual(outDim.minus, -self.baseDim.plus)
        self.assertEqual(outDim.disttype, self.baseDim.disttype)
        self.assertIsNone(outDim.PN)
        self.assertEqual(outDim.note, "Scalar shift.")

    def test_subtractFloat(self) -> None:
        outDim = self.baseDim - self.float
        self.assertEqual(outDim.nom, self.baseDim.nom - self.float)
        self.assertEqual(outDim.plus, self.baseDim.plus)
        self.assertEqual(outDim.minus, self.baseDim.minus)
        self.assertEqual(outDim.disttype, self.baseDim.disttype)
        self.assertIsNone(outDim.PN)
        self.assertEqual(outDim.note, "Scalar shift.")

    def test_subtractRightFloat(self) -> None:
        outDim = self.float - self.baseDim
        self.assertEqual(outDim.nom, self.float - self.baseDim.nom)
        self.assertEqual(outDim.plus, -self.baseDim.minus)
        self.assertEqual(outDim.minus, -self.baseDim.plus)
        self.assertEqual(outDim.disttype, self.baseDim.disttype)
        self.assertIsNone(outDim.PN)
        self.assertEqual(outDim.note, "Scalar shift.")


class TestMulNumeric(unittest.TestCase):
    def setUp(self) -> None:
        self.baseDim = StackDim(5.0, 0.1, -0.2)
        self.int = 4
        self.float = 5.3

    def test_mulInt(self) -> None:
        outDim = self.baseDim * self.int
        self.assertEqual(outDim.nom, self.baseDim.nom * self.int)
        self.assertEqual(outDim.plus, self.baseDim.plus * self.int)
        self.assertEqual(outDim.minus, self.baseDim.minus * self.int)
        self.assertEqual(outDim.disttype, self.baseDim.disttype)
        self.assertIsNone(outDim.PN)
        self.assertEqual(outDim.note, "Scalar product.")

    def test_mulRightInt(self) -> None:
        outDim = self.int * self.baseDim
        self.assertEqual(outDim.nom, self.baseDim.nom * self.int)
        self.assertEqual(outDim.plus, self.baseDim.plus * self.int)
        self.assertEqual(outDim.minus, self.baseDim.minus * self.int)
        self.assertEqual(outDim.disttype, self.baseDim.disttype)
        self.assertIsNone(outDim.PN)
        self.assertEqual(outDim.note, "Scalar product.")

    def test_mulIntCommutativity(self) -> None:
        a = self.baseDim * self.int
        b = self.int * self.baseDim
        self.assertEqual(a, b, "Failed commutativity with integer multiplication.")

    def test_mulFloat(self) -> None:
        outDim = self.baseDim * self.float
        self.assertEqual(outDim.nom, self.baseDim.nom * self.float)
        self.assertEqual(outDim.plus, self.baseDim.plus * self.float)
        self.assertEqual(outDim.minus, self.baseDim.minus * self.float)
        self.assertEqual(outDim.disttype, self.baseDim.disttype)
        self.assertIsNone(outDim.PN)
        self.assertEqual(outDim.note, "Scalar product.")

    def test_mulRightFloat(self) -> None:
        outDim = self.float * self.baseDim
        self.assertEqual(outDim.nom, self.baseDim.nom * self.float)
        self.assertEqual(outDim.plus, self.baseDim.plus * self.float)
        self.assertEqual(outDim.minus, self.baseDim.minus * self.float)
        self.assertEqual(outDim.disttype, self.baseDim.disttype)
        self.assertIsNone(outDim.PN)
        self.assertEqual(outDim.note, "Scalar product.")

    def test_mulFloatCommutativity(self) -> None:
        a = self.baseDim * self.float
        b = self.float * self.baseDim
        self.assertEqual(a, b, "Failed commutativity with float addition.")


class TestNegateStackDims(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.dim = StackDim(5.0, 0.1, -0.2, key="dim")
        self.neg_dim = -self.dim

        self.derived_dim = self.dim + self.dim
        self.neg_derived_dim = -self.derived_dim

    def test_baseNegation(self):
        # Check if the bare numbers are negated correctly
        self.assertEqual(self.dim.nom, -self.neg_dim.nom)
        self.assertEqual(self.neg_dim.plus, 0.2)
        self.assertEqual(self.neg_dim.minus, -0.1)

        # self.assertEqual(self.dim.data, -self.neg_dim.data)

        self.assertEqual(self.dim.disttype, self.neg_dim.disttype)
        self.assertEqual(self.neg_dim.note, "Inverted.")
        self.assertIsNone(self.neg_dim.PN)

        self.assertEqual(self.neg_dim.key, "-dim")

    def test_derivedNegation(self):
        # Check if the bare numbers are negated correctly
        self.assertEqual(self.derived_dim.nom, -self.neg_derived_dim.nom)
        self.assertEqual(self.neg_derived_dim.plus, 0.4)
        self.assertEqual(self.neg_derived_dim.minus, -0.2)

        self.assertTrue((self.derived_dim.data == -self.neg_derived_dim.data).all())

        self.assertEqual(self.derived_dim.disttype, self.neg_derived_dim.disttype)
        self.assertEqual(self.neg_derived_dim.note, "Derived.")
        self.assertIsNone(self.neg_derived_dim.PN)

        self.assertEqual(self.neg_derived_dim.key, "-dim+dim")


class TestAddStackDims(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.dimA = StackDim(5.0, 0.1, -0.2)
        self.dimB = StackDim(6.3, 0.5, -0.8)
        self.sum = self.dimA + self.dimB
        self.plus, self.minus = addCombination(
            (self.dimA.plus, self.dimA.minus), (self.dimB.plus, self.dimB.minus)
        )
        self.commutative_sum = self.dimB + self.dimA

    def test_nominalSum(self) -> None:
        self.assertAlmostEqual(
            self.sum.nom,
            self.dimA.nom + self.dimB.nom,
            msg="Incorrect nominal value when adding StackDims.",
        )

    def test_plusTol(self) -> None:
        self.assertAlmostEqual(
            self.sum.plus,
            self.plus,
            msg="Incorrect plus tolerance when adding StackDims.",
        )

    def test_minusTol(self) -> None:
        self.assertAlmostEqual(
            self.sum.minus,
            self.minus,
            msg="Incorrect minus tolerance when adding StackDims.",
        )

    def test_distType(self) -> None:
        self.assertEqual(
            self.sum.disttype,
            DistType.DERIVED,
            msg="Incorrect distribution type when adding StackDims.",
        )

    def test_PN(self) -> None:
        self.assertIsNone(
            self.sum.PN, msg="Incorrect part number when adding StackDims."
        )

    def test_note(self) -> None:
        self.assertEqual(
            self.sum.note, "Derived.", msg="Incorrect note when adding StackDims."
        )

    def test_commutativity(self) -> None:
        self.assertEqual(
            self.sum,
            self.commutative_sum,
            msg="Failed commutativity with StackDim addition.",
        )


class TestSubtractStackDims(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.dimA = StackDim(5.0, 0.1, -0.2)
        self.dimB = StackDim(6.3, 0.5, -0.8)
        self.sum = self.dimA - self.dimB
        self.plus, self.minus = subtractCombination(
            (self.dimA.plus, self.dimA.minus), (self.dimB.plus, self.dimB.minus)
        )

    def test_nominalSum(self) -> None:
        self.assertAlmostEqual(
            self.sum.nom,
            self.dimA.nom - self.dimB.nom,
            msg="Incorrect nominal value when subtracting StackDims.",
        )

    def test_plusTol(self) -> None:
        self.assertAlmostEqual(
            self.sum.plus,
            self.plus,
            msg="Incorrect plus tolerance when subtracting StackDims.",
        )

    def test_minusTol(self) -> None:
        self.assertAlmostEqual(
            self.sum.minus,
            self.minus,
            msg="Incorrect minus tolerance when subtracting StackDims.",
        )

    def test_distType(self) -> None:
        self.assertEqual(
            self.sum.disttype,
            DistType.DERIVED,
            msg="Incorrect distribution type when subtracting StackDims.",
        )

    def test_PN(self) -> None:
        self.assertIsNone(
            self.sum.PN, msg="Incorrect part number when subtracting StackDims."
        )

    def test_note(self) -> None:
        self.assertEqual(
            self.sum.note, "Derived.", msg="Incorrect note when subtracting StackDims."
        )


class TestMulStackDims(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.dimA = StackDim(5.0, 0.1, -0.2)
        self.dimB = StackDim(6.3, 0.5, -0.8)
        self.prod = self.dimA * self.dimB
        self.plus, self.minus = mulCombination(
            (self.dimA.nom, self.dimA.plus, self.dimA.minus),
            (self.dimB.nom, self.dimB.plus, self.dimB.minus),
        )
        self.commutative_prod = self.dimB * self.dimA

    def test_nominalProd(self) -> None:
        self.assertAlmostEqual(self.prod.nom, 31.5)

    def test_plusTol(self) -> None:
        self.assertAlmostEqual(self.prod.plus, 3.18)

    def test_minusTol(self) -> None:
        self.assertAlmostEqual(self.prod.minus, -5.1)

    def test_distType(self) -> None:
        self.assertEqual(self.prod.disttype, DistType.DERIVED)

    def test_PN(self) -> None:
        self.assertIsNone(self.prod.PN)

    def test_note(self) -> None:
        self.assertEqual(self.prod.note, "Derived.")

    def test_commutativity(self) -> None:
        self.assertEqual(self.prod, self.commutative_prod)


class TestMulNegativeStackDims(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.dimA = StackDim(5.0, 0.1, -0.2)
        self.dimB = StackDim(-6.3, 0.5, -0.8)
        self.prod = self.dimA * self.dimB
        self.plus, self.minus = mulCombination(
            (self.dimA.nom, self.dimA.plus, self.dimA.minus),
            (self.dimB.nom, self.dimB.plus, self.dimB.minus),
        )
        self.commutative_prod = self.dimB * self.dimA

    def test_nominalProd(self) -> None:
        self.assertAlmostEqual(self.prod.nom, -31.5)

    def test_plusTol(self) -> None:
        self.assertAlmostEqual(self.prod.plus, 3.66)

    def test_minusTol(self) -> None:
        self.assertAlmostEqual(self.prod.minus, -4.71)

    def test_distType(self) -> None:
        self.assertEqual(self.prod.disttype, DistType.DERIVED)

    def test_PN(self) -> None:
        self.assertIsNone(self.prod.PN)

    def test_note(self) -> None:
        self.assertEqual(self.prod.note, "Derived.")

    def test_commutativity(self) -> None:
        self.assertEqual(self.prod, self.commutative_prod)


class TestDivStackDims(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.dimA = StackDim(15.0, 0.1, -0.2)
        self.dimB = StackDim(5.0, 0.5, -0.8)
        self.result = self.dimA / self.dimB
        self.plus, self.minus = divCombination(
            (self.dimA.nom, self.dimA.plus, self.dimA.minus),
            (self.dimB.nom, self.dimB.plus, self.dimB.minus),
        )

    def test_nominal(self) -> None:
        self.assertAlmostEqual(self.result.nom, 3.0)

    def test_plusTol(self) -> None:
        self.assertAlmostEqual(self.result.plus, 0.595238095)

    def test_minusTol(self) -> None:
        self.assertAlmostEqual(self.result.minus, -0.30909090909)

    def test_distType(self) -> None:
        self.assertEqual(self.result.disttype, DistType.DERIVED)

    def test_PN(self) -> None:
        self.assertIsNone(self.result.PN)

    def test_note(self) -> None:
        self.assertEqual(self.result.note, "Derived.")


class TestStackDimSinMethod(unittest.TestCase):

    def test_sin_with_numeric_value(self):
        result = StackDim.sin(np.pi / 2)
        self.assertAlmostEqual(result.nom, 1.0)
        self.assertEqual(result.plus, 0.0)
        self.assertEqual(result.minus, 0.0)
        self.assertEqual(result.disttype, DistType.UNIFORM)

    def test_sin_with_stackdim_instance(self):
        dim = StackDim(nominal=np.pi / 4, plus=0.1, minus=-0.1, key="x")
        result = StackDim.sin(dim)

        expected_nom = np.sin(dim.nom)
        expected_plus, expected_minus = sinBounds((dim.nom, dim.plus, dim.minus))

        self.assertAlmostEqual(result.nom, expected_nom)
        self.assertAlmostEqual(result.plus, expected_plus)
        self.assertAlmostEqual(result.minus, expected_minus)
        self.assertEqual(result.disttype, DistType.DERIVED)
        self.assertEqual(result.note, "Derived.")
        self.assertEqual(result.key, f"sin({dim.key})")


class TestStackDimCosMethod(unittest.TestCase):

    def test_cos_with_numeric_value(self):
        result = StackDim.cos(np.pi / 2)
        self.assertAlmostEqual(result.nom, 0.0)
        self.assertEqual(result.plus, 0.0)
        self.assertEqual(result.minus, 0.0)
        self.assertEqual(result.disttype, DistType.UNIFORM)

    def test_cos_with_stackdim_instance(self):
        dim = StackDim(nominal=np.pi / 4, plus=0.1, minus=-0.1, key="x")
        result = StackDim.cos(dim)

        expected_nom = np.cos(dim.nom)
        expected_plus, expected_minus = cosBounds((dim.nom, dim.plus, dim.minus))

        self.assertAlmostEqual(result.nom, expected_nom)
        self.assertAlmostEqual(result.plus, expected_plus)
        self.assertAlmostEqual(result.minus, expected_minus)
        self.assertEqual(result.disttype, DistType.DERIVED)
        self.assertEqual(result.note, "Derived.")
        self.assertEqual(result.key, f"cos({dim.key})")


class TestStackDimTanMethod(unittest.TestCase):

    def test_tan_with_numeric_value(self):
        result = StackDim.tan(np.pi / 4)
        self.assertAlmostEqual(result.nom, 1.0)
        self.assertEqual(result.plus, 0.0)
        self.assertEqual(result.minus, 0.0)
        self.assertEqual(result.disttype, DistType.UNIFORM)

    def test_tan_with_stackdim_instance(self):
        dim = StackDim(nominal=np.pi / 4, plus=0.1, minus=-0.1, key="x")
        result = StackDim.tan(dim)

        expected_nom = np.tan(dim.nom)
        expected_plus, expected_minus = tanBounds((dim.nom, dim.plus, dim.minus))

        self.assertAlmostEqual(result.nom, expected_nom)
        self.assertAlmostEqual(result.plus, expected_plus)
        self.assertAlmostEqual(result.minus, expected_minus)
        self.assertEqual(result.disttype, DistType.DERIVED)
        self.assertEqual(result.note, "Derived.")
        self.assertEqual(result.key, f"tan({dim.key})")
