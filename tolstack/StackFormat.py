from tolstack.StackDim import StackDim
from tolstack.StackExpr import StackExpr
from tolstack.StackTypes import get_code_from_dist

from math import isinf


def format_constant_header():
    return f"{'ID':>10}{'VALUE':>10}  NOTE"


def format_constant(C: StackDim, usage):
    lines = []
    lines.append(f"{C.key:>10}{C.nom:>10.4g}  {C.note if C.note else ''}")
    if usage[C.key]:
        lines.append(
            f"{12*' '}Used in: {', '.join([f'{expr_key}' for expr_key in usage[C.key]])}"
        )
    return "\n".join(lines)


def format_dimension_header():
    return (
        f"{'ID':>10}{'NOMINAL':>10}{'PLUS':>8}{'MINUS':>8}{'DIST':>6}{'PN':>12}  NOTE"
    )


def format_dimension(D: StackDim, usage):
    lines = []
    lines.append(
        f"{D.key:>10}{D.nom:10.4g}{D.plus:+8.4g}{D.minus:+8.4g}"
        + f"{get_code_from_dist(D.disttype):>6}{D.PN if D.PN else '':>12}  {D.note if D.note else ''}"
    )
    if usage[D.key]:
        lines.append(
            f"{12*' '}Used in: {', '.join([f'{expr_key}' for expr_key in usage[D.key]])}"
        )
    return "\n".join(lines)


def format_expression(E: StackExpr):
    lines = []
    lines.append(f"{E.key:>5}: {E.note}")
    lines.append(f"{7*' '}Expression: {E.expr:<15}  Expansion: {E.expand()}")
    lines.append(f"{7*' '}Evaluation Method: {E.method}")
    _val = E.evaluate()
    lines.append(f"{7*' '}Nominal: {_val.nom:15.4g}")
    lines.append(
        f"{7*' '}Value:   {_val.center(E.method):15.4g} {_val.upper_tol(E.method):+.4g} {_val.lower_tol(E.method):+.4g}"
    )

    if not isinf(E.lower):
        _pass = E.lower < _val.lower(E.method)
        lines.append(
            f"{'' if _pass else '**':<9}Lower Bound:{E.lower:10.4g}  {'PASS' if _pass else f'FAIL: {_val.lower(E.method):.4g}'}"
        )
    else:
        lines.append(f"{9*' '}Lower Bound:{'NONE':>10}  PASS")

    if not isinf(E.upper):
        _pass = E.upper > _val.upper(E.method)
        lines.append(
            f"{'' if _pass else '**':<9}Upper Bound:{E.upper:10.4g}  {'PASS' if _pass else f'FAIL: {_val.upper(E.method):.4g}'}"
        )
    else:
        lines.append(f"{9*' '}Upper Bound:{'NONE':>10}  PASS")

    return "\n".join(lines)
