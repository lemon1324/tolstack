from tolstack.StackDim import StackDim
from tolstack.StackExpr import StackExpr
from tolstack.StackTypes import get_code_from_dist
from tolstack.StackParser import StackParser

from tolstack.StackUtils import word_wrap

from tolstack.gui.GUITypes import *

from math import isinf, isclose

import re

FORMAT_WIDTH = 80


# info as defined by the gui get_info method
def format_text(parser: StackParser, info):
    print_lines = []

    value_map = parser.constants | parser.dimensions

    # Print Analysis Info
    print_lines.append(f"{info[AnalysisWidget.TITLE].upper()}")
    print_lines.append(
        f"{info[AnalysisWidget.DOCNO]}{'-' if info[AnalysisWidget.DOCNO] else 'Rev. '}{info[AnalysisWidget.REVISION]}\n"
    )
    print_lines.append(info[AnalysisWidget.DESCRIPTION])
    print_lines.append("\n")

    # Print document units
    print_lines.append(f"THIS DOCUMENT IN {info[OptionsWidget.UNITS].upper()}.\n")

    if parser.constants:
        print_lines.append("CONSTANTS:")
        print_lines.append(format_constant_header())
        for key, C in parser.constants.items():
            print_lines.append(format_constant(C))
            if info[OptionsWidget.WHERE_USED] and C.key in parser.where_used:
                print_lines.append(format_usage(C, parser.where_used))
        print_lines.append("\n")

    if parser.dimensions:
        print_lines.append("DIMENSIONS:")
        print_lines.append(format_dimension_header())
        for key, D in parser.dimensions.items():
            print_lines.append(format_dimension(D))
            if info[OptionsWidget.WHERE_USED] and D.key in parser.where_used:
                print_lines.append(format_usage(D, parser.where_used))
        print_lines.append("\n")

    if parser.expressions:
        print_lines.append("EXPRESSION SUMMARY:")
        for key, SE in parser.expressions.items():
            print_lines.append(format_expression_summary(SE))

        print_lines.append("\n")

        print_lines.append("EXPRESSIONS:")
        for key, SE in parser.expressions.items():
            print_lines.append(format_expression(SE))

            if info[OptionsWidget.SENSITIVITY]:
                s = SE.sensitivities()
                print_lines.append(format_sensitivity(SE, s))

            if info[OptionsWidget.CONTRIBUTIONS]:
                c = SE.contributions()
                print_lines.append(format_contribution(SE, c))
            print_lines[-1] = print_lines[-1] + "\n"

    return print_lines


def format_constant_header():
    return f"{'ID':>10}{'VALUE':>10}  NOTE"


def format_constant(C: StackDim):
    return word_wrap(
        f"{C.key:>10}{format_shortest(C.nom, 4):>10}  {C.note if C.note else ''}",
        FORMAT_WIDTH,
        22,
    )


def format_dimension_header():
    return f"{'ID':>10}{'NOMINAL':>9}{'PLUS':>9}{'MINUS':>9}{'D':>4}{'PN':>12}  NOTE"


def format_dimension(D: StackDim):
    return word_wrap(
        f"{D.key:>10}{format_shortest(D.nom,3):>9}{format_shortest(D.plus,3):>9}{format_shortest(D.minus,3):>9}"
        + f"{get_code_from_dist(D.disttype):>4}{D.PN if D.PN else '':>12}  {D.note if D.note else ''}",
        FORMAT_WIDTH,
        55,
    )


def format_usage(K: StackDim, usage):
    if usage[K.key]:
        return word_wrap(
            f"{12*' '}Used in: {', '.join([f'{expr_key}' for expr_key in usage[K.key]])}",
            FORMAT_WIDTH,
            21,
        )

    return ""


def format_expression_summary(E: StackExpr):
    lines = []
    lines.append(word_wrap(f"{E.key:>5}: {E.note}", FORMAT_WIDTH, 7))

    return "\n".join(lines)


def format_expression(E: StackExpr):
    lines = []
    lines.append(word_wrap(f"{E.key:>5}: {E.note}", FORMAT_WIDTH, 7))
    lines.append(
        word_wrap(
            f"{7*' '}Expression: {E.expr}",
            FORMAT_WIDTH,
            19,
        )
    )
    lines.append(
        word_wrap(
            f"{7*' '}Expansion:  {E.expand()}",
            FORMAT_WIDTH,
            19,
        )
    )
    lines.append(f"{7*' '}Evaluation: {E.method}")
    _val = E.evaluate()
    lines.append(f"{7*' '}Nominal: {format_shortest(_val.nom,3):>15}")
    lines.append(
        f"{7*' '}Value:   {format_shortest(_val.center(E.method),3):>15} {format_shortest(_val.upper_tol(E.method),2)} {format_shortest(_val.lower_tol(E.method),2)}"
    )

    if not isinf(E.lower) and not isinf(E.upper):
        if not isinf(E.lower):
            _pass = E.lower <= _val.lower(E.method) or isclose(
                E.lower, _val.lower(E.method), abs_tol=1e-9
            )
            lines.append(
                f"{'' if _pass else '***':<9}Lower Bound:{E.lower:10.4g}  {'PASS' if _pass else f'FAIL: {format_shortest(_val.lower(E.method),3)}'}"
            )
        else:
            lines.append(f"{9*' '}Lower Bound:{'NONE':>10}  PASS")

        if not isinf(E.upper):
            _pass = E.upper >= _val.upper(E.method) or isclose(
                E.upper, _val.upper(E.method), abs_tol=1e-9
            )
            lines.append(
                f"{'' if _pass else '***':<9}Upper Bound:{E.upper:10.4g}  {'PASS' if _pass else f'FAIL: {format_shortest(_val.upper(E.method),3)}'}"
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
            f"{'∂/∂'+var:>16}: {format_shortest(partial,2):>10} {format_center_bar(partial/scale)}"
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
        lines.append(
            f"{var:>16}: {f'±{format_shortest(tol,2)[1:]}'.rjust(10)} {format_bar(tol/scale)}"
        )

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


# format to a certain number of significant figures, either scientific or normal, whichever is shorter
def format_shortest(num, sig_figs, leading_zeroes=False):
    scientific = format_scientific(num, sig_figs - 1, 1)
    decimal = format_significant_figures(num, sig_figs, leading_zeroes)

    return scientific if len(scientific) < len(decimal) else decimal


# Custom formatting to control the number of digits in the exponent
def format_scientific(num, precision=4, exp_digits=2):
    formatted = f"{num:+.{precision}e}"
    parts = formatted.split("e")
    exponent = int(parts[1])
    sign = "+" if exponent >= 0 else "-"
    fmt_exponent = f"e{sign}{abs(exponent):0{exp_digits}d}"
    return parts[0] + fmt_exponent


# Custom formatting to "actually" print to a set number of sig figs
# There doesn't seem to be a better way to actually do sig figs?
# Apparently to get it right I have to actually process it as a decimal >_>
def format_significant_figures(num, sig_figs, leading_zeros=False):
    # convert to string
    num_str = f"{num:+.{2*sig_figs}f}"

    # remove and store sign symbol
    sign = ""
    if num_str[0] in "+-":
        sign = num_str[0]
        num_str = num_str[1:]

    # split into integer and fractional parts
    if "." in num_str:
        int_part, frac_part = num_str.split(".")
    else:
        int_part, frac_part = (num_str, "")

    # Remove leading zeros in integer part
    int_part = int_part.lstrip("0")
    int_len = len(int_part)
    frac_len = len(frac_part)

    # Combine into one continuous number for ease of counting significant figures
    combined = int_part + frac_part

    if int_len > 0:
        # Truncate to required significant figures
        truncated_combined = round_string(combined, sig_figs)

        # place the decimal point correctly
        if sig_figs < int_len:
            result = f"{sign}{truncated_combined}{'0' * (int_len-sig_figs)}"
        else:
            result = (
                f"{sign}{truncated_combined[:int_len]}.{truncated_combined[int_len:]}"
            )
    else:  # magnitude less than one
        lead = "0" if leading_zeros else ""

        match = re.search(r"[1-9]", combined)
        if not match:
            # number is apparently zero, so return that many places after the decimal
            result = f"{sign}{lead}.{'0'*sig_figs}"
        else:
            first_digit = match.start()
            pad = (
                "0" * ((first_digit + sig_figs) - frac_len)
                if first_digit + sig_figs > frac_len
                else ""
            )

            result = f"{sign}{lead}.{frac_part[:first_digit+sig_figs]}{pad}"

    return result


def round_string(num_str, digits):
    if len(num_str) <= digits:
        return num_str

    # Determine if rounding is needed
    if num_str[digits] in "56789":
        # Increment the last character before the cut if it's not '9'
        if num_str[digits - 1] != "9":
            rounded_char = chr(ord(num_str[digits - 1]) + 1)
            return num_str[: digits - 1] + rounded_char
        else:
            # Rounding '9' needs handling differently
            result = list(num_str[:digits])
            i = digits - 1
            while i >= 0 and result[i] == "9":
                result[i] = "0"
                i -= 1
            if i >= 0:
                result[i] = chr(ord(result[i]) + 1)
            else:
                result.insert(0, "1")
            return "".join(result)
    else:
        return num_str[:digits]
