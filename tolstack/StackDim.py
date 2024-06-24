# Dimension that can be part of a linear tolerance stack

from __future__ import annotations

from numpy.random import default_rng
from numpy import ndarray
from numpy import full
from numpy import quantile

from math import isclose

from scipy import stats

from tolstack.StackTypes import DistType, get_code_from_dist, EvalType

import sys


class StackDim:
    rng = default_rng()
    N = 100000

    def __init__(
        self,
        nominal: float,
        plus: float = 0.0,
        minus: float = 0.0,
        disttype: DistType = DistType.UNIFORM,
        distribution: ndarray = None,
        PN: str = None,
        note: str = None,
        key: str = "",
    ) -> None:
        self.nom = nominal
        self.plus = plus
        self.minus = minus

        if self.plus - self.minus < 0:
            print("add error, but the +tol is less than the -tol")

        self.disttype = disttype
        if disttype is DistType.DERIVED:
            self.data = distribution
        else:
            self.data = self.dist()

        self.PN = PN
        self.note = note

        self.key = key

    def dist(self) -> ndarray:
        match self.disttype:
            case DistType.UNIFORM:
                return self._uniformDist()

            case DistType.NORMAL_1S:
                return self._normalDist(1)

            case DistType.NORMAL_2S:
                return self._normalDist(2)

            case DistType.NORMAL_3S:
                return self._normalDist(3)

            case DistType.CONSTANT:
                return full((1, StackDim.N), self.nom)

            case _:
                return self.rng.permutation(self.data)

    def center(self, method: EvalType) -> float:
        match method:
            case EvalType.WORSTCASE:
                return self.nom
            case (
                EvalType.STATISTICAL_1S
                | EvalType.STATISTICAL_2S
                | EvalType.STATISTICAL_3S
            ):
                return quantile(self.data, 0.5, method="median_unbiased")
            case _:
                sys.exit(f"Error: cannot evaluate a center value with {method} method.")

    def lower(self, method: EvalType) -> float:
        match method:
            case EvalType.WORSTCASE:
                return self.nom + self.minus
            case EvalType.STATISTICAL_1S:
                return quantile(self.data, stats.norm.sf(1), method="median_unbiased")
            case EvalType.STATISTICAL_2S:
                return quantile(self.data, stats.norm.sf(2), method="median_unbiased")
            case EvalType.STATISTICAL_3S:
                return quantile(self.data, stats.norm.sf(3), method="median_unbiased")
            case _:
                sys.exit(f"Error: cannot evaluate a lower bound with {method} method.")

    def lower_tol(self, method: EvalType) -> float:
        return self.lower(method) - self.center(method)

    def upper(self, method: EvalType) -> float:
        match method:
            case EvalType.WORSTCASE:
                return self.nom + self.plus
            case EvalType.STATISTICAL_1S:
                return quantile(self.data, stats.norm.cdf(1), method="median_unbiased")
            case EvalType.STATISTICAL_2S:
                return quantile(self.data, stats.norm.cdf(2), method="median_unbiased")
            case EvalType.STATISTICAL_3S:
                return quantile(self.data, stats.norm.cdf(3), method="median_unbiased")
            case _:
                sys.exit(f"Error: cannot evaluate a lower bound with {method} method.")

    def upper_tol(self, method: EvalType) -> float:
        return self.upper(method) - self.center(method)

    def _uniformDist(self) -> ndarray:
        _low = self.nom + self.minus
        _high = self.nom + self.plus
        return self.rng.uniform(_low, _high, (1, StackDim.N))

    def _normalDist(self, scale) -> ndarray:
        _mu = self.nom + 0.5 * (self.plus + self.minus)  # center of range, not nominal
        _sig = (self.plus - self.minus) / (2 * scale)  # 2x for +/- sigma
        return self.rng.normal(_mu, _sig, (1, StackDim.N))

    @staticmethod
    def _addStackDims(first: StackDim, second: StackDim) -> StackDim:
        _key = first.key + "+" + second.key
        _nom = first.nom + second.nom
        _plus = first.plus + second.plus
        _minus = first.minus + second.minus
        _sample = first.dist() + second.dist()
        _type = DistType.DERIVED
        return StackDim(_nom, _plus, _minus, _type, _sample, note="Derived.", key=_key)

    @staticmethod
    def _addNumeric(dim: StackDim, number: float) -> StackDim:
        _key = dim.key + "+" + str(number)
        _nom = dim.nom + number
        _plus = dim.plus
        _minus = dim.minus
        _sample = dim.dist() + number
        _type = dim.disttype
        return StackDim(
            _nom, _plus, _minus, _type, _sample, note="Scalar shift.", key=_key
        )

    def __str__(self) -> str:
        if self.disttype == DistType.CONSTANT:
            return f"{self.nom:10.4g} {self.note if self.note is not None else ''}"
        else:
            return f"{self.nom:10.4g}{self.plus:+8.4g}{self.minus:+8.4g}{get_code_from_dist(self.disttype):>5}{self.PN if self.PN is not None else '':>10} {self.note if self.note is not None else ''}"

    def __eq__(self, other) -> bool:
        """
        Overload the equality test for StackDim

        :param self: This StackDim.
        :param other: Another object.
        :returns: True if both objects are StackDims, and have identical nominal, plus, minus values, and distribution types. False otherwise.
        """
        if not isinstance(other, self.__class__):
            return False
        if self.disttype != other.disttype:
            return False
        if not isclose(self.nom, other.nom, abs_tol=1e-9):
            return False
        if not isclose(self.plus, other.plus, abs_tol=1e-9):
            return False
        if not isclose(self.minus, other.minus, abs_tol=1e-9):
            return False
        return True

    def __neg__(self) -> StackDim:
        _nom = -self.nom
        _plus = -self.minus
        _minus = -self.plus
        _type = self.disttype
        _sample = -self.dist()
        _note = "Derived." if self.note == "Derived." else "Inverted."
        _key = "-" + self.key

        return StackDim(_nom, _plus, _minus, _type, _sample, note=_note, key=_key)

    def __add__(self, other) -> StackDim:
        if isinstance(other, self.__class__):
            return StackDim._addStackDims(self, other)
        elif isinstance(other, (int, float)):
            return StackDim._addNumeric(self, other)
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{self.__class__}' and '{type(other)}'"
            )

    def __radd__(self, other) -> StackDim:
        # implements (other + self)
        # since addition of StackDims and/or scalars commutes,
        # simply flip such that we can use the __add__ method.
        return self + other

    def __sub__(self, other) -> StackDim:
        # implements (self - other)
        # leverage negation definition to implement as self + (-other)
        return self + (-other)

    def __rsub__(self, other) -> StackDim:
        # implements (other - self)
        # leverage negation definition to implement as (-self) + other
        return -self + other
