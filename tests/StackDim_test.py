import unittest

from tolstack.StackDim import StackDim
from tolstack.StackTypes import DistType

from tests.TestUtils import addCombination
from tests.TestUtils import subtractCombination


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
