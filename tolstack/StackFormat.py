from tolstack.StackDim import StackDim
from tolstack.StackExpr import StackExpr
from tolstack.StackTypes import get_code_from_dist

from tolstack.StackUtils import word_wrap

from math import isinf, isclose

FORMAT_WIDTH = 80


def format_constant_header():
    return f"{'ID':>10}{'VALUE':>10}  NOTE"


def format_constant(C: StackDim):
    return word_wrap(
        f"{C.key:>10}{C.nom:>10.4g}  {C.note if C.note else ''}", FORMAT_WIDTH, 22
    )


def format_dimension_header():
    return f"{'ID':>10}{'NOMINAL':>10}{'PLUS':>8}{'MINUS':>8}{'D':>4}{'PN':>12}  NOTE"


def format_dimension(D: StackDim):
    return word_wrap(
        f"{D.key:>10}{D.nom:10.4g}{D.plus:+8.4g}{D.minus:+8.4g}"
        + f"{get_code_from_dist(D.disttype):>4}{D.PN if D.PN else '':>12}  {D.note if D.note else ''}",
        FORMAT_WIDTH,
        54,
    )


def format_usage(K: StackDim, usage):
    if usage[K.key]:
        return word_wrap(
            f"{12*' '}Used in: {', '.join([f'{expr_key}' for expr_key in usage[K.key]])}",
            FORMAT_WIDTH,
            21,
        )

    return ""


def format_expression(E: StackExpr):
    lines = []
    lines.append(word_wrap(f"{E.key:>5}: {E.note}", FORMAT_WIDTH, 7))
    lines.append(
        word_wrap(
            f"{7*' '}Expression: {E.expr}",
            FORMAT_WIDTH,
            47,
        )
    )
    lines.append(
        word_wrap(
            f"{7*' '}Expansion:  {E.expand()}",
            FORMAT_WIDTH,
            47,
        )
    )
    lines.append(f"{7*' '}Evaluation: {E.method}")
    _val = E.evaluate()
    lines.append(f"{7*' '}Nominal: {_val.nom:15.4g}")
    lines.append(
        f"{7*' '}Value:   {_val.center(E.method):15.4g} {_val.upper_tol(E.method):+.4g} {_val.lower_tol(E.method):+.4g}"
    )

    if not isinf(E.lower):
        _pass = E.lower <= _val.lower(E.method) or isclose(
            E.lower, _val.lower(E.method), abs_tol=1e-9
        )
        lines.append(
            f"{'' if _pass else '***':<9}Lower Bound:{E.lower:10.4g}  {'PASS' if _pass else f'FAIL: {_val.lower(E.method):.4g}'}"
        )
    else:
        lines.append(f"{9*' '}Lower Bound:{'NONE':>10}  PASS")

    if not isinf(E.upper):
        _pass = E.upper >= _val.upper(E.method) or isclose(
            E.upper, _val.upper(E.method), abs_tol=1e-9
        )
        lines.append(
            f"{'' if _pass else '***':<9}Upper Bound:{E.upper:10.4g}  {'PASS' if _pass else f'FAIL: {_val.upper(E.method):.4g}'}"
        )
    else:
        lines.append(f"{9*' '}Upper Bound:{'NONE':>10}  PASS")

    return "\n".join(lines)


def format_sensitivity(E: StackExpr, sensitivities):
    lines = []

    lines.append(f"{7*' '}Sensitivities:")

    scale = max(abs(val) for val in sensitivities.values())

    # avoid division by zero in format
    # If scale is zero then all items are near zero so scale doesn't matter.
    if isclose(scale, 0, abs_tol=1e-9):
        scale = 1

    for var, partial in sensitivities.items():
        lines.append(
            f"{'∂/∂'+var:>16}: {partial:10.2g} {format_center_bar(partial/scale)}"
        )

    return "\n".join(lines)


def format_contribution(E: StackExpr, contributions):
    lines = []

    lines.append(f"{7*' '}Contributions:")

    scale = max(abs(val) for val in contributions.values())

    # avoid division by zero in format
    # If scale is zero then all items are near zero so scale doesn't matter.
    if isclose(scale, 0, abs_tol=1e-9):
        scale = 1

    for var, tol in contributions.items():
        lines.append(f"{var:>16}: {f'±{tol:.3g}'.rjust(10)} {format_bar(tol/scale)}")

    return "\n".join(lines)


def format_bar(number, width=19) -> str:
    if not 0 <= number <= 1:
        raise ValueError("The number must be in the range [0, 1]")

    bar = ["=" if i + 1 / 2 < number * width else " " for i in range(width)]

    return f"[{''.join(bar)}]"


def format_center_bar(number, width=19) -> str:
    if not -1 <= number <= 1:
        raise ValueError("The number must be in the range [-1, 1]")

    if width % 2 == 0:
        width += 1

    dir = 1 if number > 0 else -1

    bar = [" "] * width
    center = width // 2
    for i in range(center, center + dir + int(number * (width // 2)), dir):
        bar[i] = "="

    bar[center] = "|"

    return f"[{''.join(bar)}]"


if __name__ == "__main__":
    for n in [-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1]:
        print(format_center_bar(n, 6))

    for n in [0, 0.25, 0.5, 0.75, 1]:
        print(format_bar(n, 9))
