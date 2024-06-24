import unittest

from tolstack.StackDim import StackDim
from tolstack.StackExpr import StackExpr


class TestStackExprListValidate(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        self.E1 = StackExpr("D1+D2+D3")
        self.E2 = StackExpr("D3-(E1-D5)")
        self.E3 = StackExpr("E3 - (E2-E1)")
