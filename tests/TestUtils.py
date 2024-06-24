import numpy as np


def addCombination(
    a: tuple[float, float], b: tuple[float, float]
) -> tuple[float, float]:
    """
    Utility function to explicitly compute min/max combinations of tolerances.

        :param a: a 2-tuple of the plus and minus tolerances for a StackDim.
        :param b: a 2-tuple of the plus and minus tolerances for a second StackDim.
        :returns: A 2-tuple containing the plus and minus tolerances of the result of adding the two StackDims.
    """
    # all 4 combinations of tolerances
    sums = np.array([a[0], a[0], a[1], a[1]]) + np.array([b[0], b[1], b[0], b[1]])
    return (max(sums), min(sums))


def subtractCombination(
    a: tuple[float, float], b: tuple[float, float]
) -> tuple[float, float]:
    """
    Utility function to explicitly compute min/max combinations of tolerances.

    Subtracts b from a.

        :param a: a 2-tuple of the plus and minus tolerances for a StackDim.
        :param b: a 2-tuple of the plus and minus tolerances for a second StackDim.
        :returns: A 2-tuple containing the plus and minus tolerances of the result of subtracting b from a.
    """
    # all 4 combinations of tolerances
    sums = np.array([a[0], a[0], a[1], a[1]]) - np.array([b[0], b[1], b[0], b[1]])
    return (max(sums), min(sums))
