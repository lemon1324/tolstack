# Dimension that can be part of a linear tolerance stack

from __future__ import annotations

from numpy.random import default_rng
from numpy import ndarray
from numpy import full
from numpy import quantile

from math import isclose

from scipy.stats import norm

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
        """
        Returns the underlying distribution of this StackDim for Monte Carlo propagation.

        If the distribution type is a known analytical distribution, then select a new sample from that
        distribution using the numpy random number generator. If the distribution is already a simulated
        distribution from an operation on StackDims, then return a random permutation of the distribution.
        Since mathematical operations on StackDims are performed elementwise, this simulates random sampling
        from the unknown distribution as long as d << StackDim.N, where StackDim.N is the number of points
        sampled, and d is the maximum depth of an expression tree containing this StackDim.

        Returns:
        ndarray
            The underlying distribution for Monte Carlo propagation.
        """
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
        """
        Returns the center value for reports.

        When using worst case analysis, this will return the nominal value, which will in general
        not be centered within the tolerance limits. When using statistical analysis, returns the
        median value of the distribution.

        Parameters:
        method (EvalType): The evaluation method used for tolerance analysis.

        Returns:
        float: The center value based on the provided evaluation method.
        """
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
        """
        Returns the lower value for reports.

        This returns the lower edge of the tolerance band. When using worst case analysis, this will
        return the nominal value offset by the minus tolerance. When using statistical analysis, returns
        the quantile corresponding to the selected sigma value.

        Parameters:
        method (EvalType): The evaluation method used for tolerance analysis.

        Returns:
        float: The lower tolerance limit based on the provided evaluation method.
        """
        match method:
            case EvalType.WORSTCASE:
                return self.nom + self.minus
            case EvalType.STATISTICAL_1S:
                return quantile(self.data, norm.sf(1), method="median_unbiased")
            case EvalType.STATISTICAL_2S:
                return quantile(self.data, norm.sf(2), method="median_unbiased")
            case EvalType.STATISTICAL_3S:
                return quantile(self.data, norm.sf(3), method="median_unbiased")
            case _:
                sys.exit(f"Error: cannot evaluate a lower bound with {method} method.")

    def lower_tol(self, method: EvalType) -> float:
        """
        Returns the lower tolerance for reports.

        This returns the lower tolerance value, as measured by the tolerance value applied to the center
        value in order to reach the lower bound.

        Parameters:
        method (EvalType): The evaluation method used for tolerance analysis.

        Returns:
        float: The lower tolerance value based on the provided evaluation method.
        """
        return self.lower(method) - self.center(method)

    def upper(self, method: EvalType) -> float:
        """
        Returns the upper value for reports.

        This returns the upper edge of the tolerance band. When using worst case analysis, this will
        return the nominal value offset by the plus tolerance. When using statistical analysis, returns
        the quantile corresponding to the selected sigma value.

        Parameters:
        method (EvalType): The evaluation method used for tolerance analysis.

        Returns:
        float: The upper tolerance limit based on the provided evaluation method.
        """
        match method:
            case EvalType.WORSTCASE:
                return self.nom + self.plus
            case EvalType.STATISTICAL_1S:
                return quantile(self.data, norm.cdf(1), method="median_unbiased")
            case EvalType.STATISTICAL_2S:
                return quantile(self.data, norm.cdf(2), method="median_unbiased")
            case EvalType.STATISTICAL_3S:
                return quantile(self.data, norm.cdf(3), method="median_unbiased")
            case _:
                sys.exit(f"Error: cannot evaluate a lower bound with {method} method.")

    def upper_tol(self, method: EvalType) -> float:
        """
        Returns the upper tolerance for reports.

        This returns the upper tolerance value, as measured by the tolerance value applied to the center
        value in order to reach the upper bound.

        Parameters:
        method (EvalType): The evaluation method used for tolerance analysis.

        Returns:
        float: The upper tolerance value based on the provided evaluation method.
        """
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
        """
        Implements (self + other).

        Splits implementation based on whether other is a StackDim or if it is a numeric value.

        Parameters:
        other: Any
            The value to add to this instance.

        Returns:
        StackDim
            The result of the addition.
        """
        if isinstance(other, self.__class__):
            return StackDim._addStackDims(self, other)
        elif isinstance(other, (int, float)):
            return StackDim._addNumeric(self, other)
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{self.__class__}' and '{type(other)}'"
            )

    def __radd__(self, other) -> StackDim:
        """
        Implements (other + self).

        Since the addition of StackDims and/or scalars commutes,
        this method simply flips the operation so that the __add__ method can be used.

        Parameters:
        other: Any
            The value to add to this instance.

        Returns:
        StackDim
            The result of the addition.
        """
        return self + other

    def __sub__(self, other) -> StackDim:
        """
        Implements (self - other).

        Leverages the negation definition to implement this as self + (-other).

        Parameters:
        other: Any
            The value to subtract from this instance.

        Returns:
        StackDim
            The result of the subtraction.
        """
        return self + (-other)

    def __rsub__(self, other) -> StackDim:
        """
        Implements (other - self).

        Leverages negation definition to implement as (-self) + other.

        Parameters:
        other: Any
            The value to subtract from this instance.

        Returns:
        StackDim
            The result of the subtraction.
        """
        return -self + other
