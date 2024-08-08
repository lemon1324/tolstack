# Standard Library Imports
from io import BytesIO
import os
from pathlib import Path
from PIL import Image as PILImage
from collections import defaultdict
from collections.abc import Iterable
from math import isinf, isclose

# Third-Party Library Imports
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Image,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
)

# Local Application Imports
from tolstack.gui.GUITypes import AnalysisWidget, DataWidget, OptionsWidget
from tolstack.gui.CustomPDFElements import TitleFlowable
from tolstack.gui.PDFStyles import PDFStyles, update_paragraph_style
from tolstack.StackParser import StackParser
from tolstack.gui.FormatText import format_shortest
from tolstack.StackTypes import get_code_from_dist
from tolstack.StackExpr import StackExpr
from tolstack.StackDim import StackDim

# TODO: imports only for debugging, remove later
from tolstack.gui.FileIO import open_from_name, get_absolute_path


# Primary function to format and generate the PDF
def format_pdf(output_filename: str, parser: StackParser, info):
    doc = SimpleDocTemplate(output_filename, pagesize=letter)

    contents = create_content_elements(parser, info)

    doc.build(contents)


def create_content_elements(parser: StackParser, info):
    contents = []

    # Generate top matter
    append_or_extend(contents, create_title(info))
    append_or_extend(contents, create_document_number(info))
    append_or_extend(contents, create_document_description(info))
    append_or_extend(contents, create_units_note(info))
    append_or_extend(contents, Spacer(0, 20))

    # Summaries
    if parser.constants:
        append_or_extend(contents, create_constants_summary(parser, info))

    # TODO: add a toggle option to be able to enable/disable detailed vs brief summary for dims
    # append_or_extend(contents, create_dimension_summary(parser, info))
    append_or_extend(contents, create_dimension_table(parser, info))

    # TODO: add options flag to enable/disable expression summaries
    append_or_extend(contents, create_expression_summary(parser, info))

    # Details of dimension definitions
    if info[OptionsWidget.FIND_IMAGES]:
        append_or_extend(contents, PageBreak())
        append_or_extend(contents, create_dimension_details(parser, info))

    # Expressions
    append_or_extend(contents, PageBreak())
    append_or_extend(contents, create_expression_details(parser, info))

    # DEBUG
    # expr = parser.expressions["E1"]
    # value = expr.evaluate()
    # append_or_extend(contents, create_tolerance_table(expr, value))
    # append_or_extend(contents, create_expression_details(parser, info))
    # append_or_extend(contents, create_single_expression(parser.expressions["E6"], info))

    # append_or_extend(
    #     contents, generate_center_bar_image(0.95, width=3 * inch, height=40)
    # )
    # append_or_extend(contents, generate_bar_image(0.35, width=3 * inch, height=40))

    return contents


def create_title(info):
    return Paragraph(info[AnalysisWidget.TITLE], PDFStyles["TitleStyle"])


def create_document_number(info):
    doc_string = f"{info[AnalysisWidget.DOCNO]}{'-' if info[AnalysisWidget.DOCNO] else 'Rev. '}{info[AnalysisWidget.REVISION]}"
    return Paragraph(doc_string, PDFStyles["DocNoStyle"])


def create_document_description(info):
    style = PDFStyles["BodyStyle"]
    lines = info[AnalysisWidget.DESCRIPTION].split("\n")
    paragraphs = [Paragraph(line, style) for line in lines]

    paragraphs.append(Spacer(0, 15))

    return paragraphs


def create_units_note(info):
    unit_string = f"THIS DOCUMENT IN {info[OptionsWidget.UNITS].upper()}"
    return Paragraph(unit_string, PDFStyles["SectionHeaderStyle"])


def create_constants_summary(parser: StackParser, info):
    elements = []

    # Section title
    elements.append(Paragraph("CONSTANTS:", PDFStyles["SectionHeaderStyle"]))

    # Constants Table
    headers = [["ID", "Value", "Note"]]
    data = []
    style = TableStyle(
        [
            ("ALIGN", (0, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("VALIGN", (0, 1), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (1, -1), 2),
            ("RIGHTPADDING", (0, 0), (0, -1), 2),
        ]
    )

    for C in parser.constants.values():
        row = [
            C.key,
            format_shortest(C.nom, 4),
            Paragraph(C.note if C.note else "", PDFStyles["PlainStyle"]),
        ]
        data.append(row)

        if info[OptionsWidget.WHERE_USED] and C.key in parser.where_used:
            usagetext = f"Used in: {', '.join([f'{expr_key}' for expr_key in sorted(parser.where_used[C.key])])}"
            data.append(["", "", Paragraph(usagetext, PDFStyles["PlainStyle"])])
            style.add("BOTTOMPADDING", (0, len(data) - 1), (-1, len(data) - 1), 0)
            style.add("BOTTOMPADDING", (0, len(data)), (-1, len(data)), 5)
            style.add("NOSPLIT", (0, len(data) - 1), (-1, len(data)))

    full_data = headers + data

    col_widths = [0.5 * inch, 0.75 * inch, 0 * inch]
    col_widths[-1] = (letter[0] - 2 * inch) - sum(col_widths[:-1])

    table = Table(full_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(style)
    elements.append(table)

    elements.append(Spacer(0, 20))

    return elements


def create_dimension_summary(parser: StackParser, info):
    elements = []

    # Section title
    elements.append(Paragraph("DIMENSIONS SUMMARY:", PDFStyles["SectionHeaderStyle"]))

    # Dimension Summary Table
    headers = [["ID", "Note"]]
    data = []
    style = TableStyle(
        [
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("VALIGN", (0, 1), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (0, -1), 2),
            ("RIGHTPADDING", (0, 0), (0, -1), 2),
            ("LEFTPADDING", (1, 0), (-1, -1), 10),
        ]
    )

    for D in parser.dimensions.values():
        row = [
            D.key,
            Paragraph(D.note if D.note else "", PDFStyles["PlainStyle"]),
        ]
        data.append(row)

        if info[OptionsWidget.WHERE_USED] and D.key in parser.where_used:
            usagetext = f"Used in: {', '.join([f'{expr_key}' for expr_key in sorted(parser.where_used[D.key])])}"
            data.append(["", Paragraph(usagetext, PDFStyles["PlainStyle"])])
            style.add("BOTTOMPADDING", (0, len(data) - 1), (-1, len(data) - 1), 0)
            style.add("BOTTOMPADDING", (0, len(data)), (-1, len(data)), 5)
            style.add("NOSPLIT", (0, len(data) - 1), (-1, len(data)))

    full_data = headers + data

    col_widths = [0.5 * inch, 0 * inch]
    col_widths[-1] = (letter[0] - 2 * inch) - sum(col_widths[:-1])

    table = Table(full_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(style)
    elements.append(table)

    elements.append(Spacer(0, 20))

    return elements


def create_dimension_table(parser: StackParser, info):
    elements = []

    # Section title
    elements.append(Paragraph("DIMENSION SUMMARY:", PDFStyles["SectionHeaderStyle"]))

    # Dimension Summary Table
    headers = [["ID", "Nom.", "+", "-", "D", "PN", "Note"]]
    data = []
    style = TableStyle(
        [
            ("ALIGN", (0, 0), (5, -1), "RIGHT"),
            ("ALIGN", (4, 0), (4, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("VALIGN", (0, 1), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (5, -1), 2),
            ("RIGHTPADDING", (0, 0), (4, -1), 2),
        ]
    )

    for D in parser.dimensions.values():
        row = [
            D.key,
            format_shortest(D.nom, 4),
            format_shortest(D.plus, 3),
            format_shortest(D.minus, 3),
            get_code_from_dist(D.disttype),
            D.PN if D.PN else "",
            Paragraph(D.note if D.note else "", PDFStyles["PlainStyle"]),
        ]
        data.append(row)

        if info[OptionsWidget.WHERE_USED] and D.key in parser.where_used:
            usagetext = f"Used in: {', '.join([f'{expr_key}' for expr_key in sorted(parser.where_used[D.key])])}"
            data.append(
                [
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    Paragraph(usagetext, PDFStyles["PlainStyle"]),
                ]
            )
            style.add("BOTTOMPADDING", (0, len(data) - 1), (-1, len(data) - 1), 0)
            style.add("BOTTOMPADDING", (0, len(data)), (-1, len(data)), 5)
            style.add("NOSPLIT", (0, len(data) - 1), (-1, len(data)))

    full_data = headers + data

    col_widths = [
        0.5 * inch,
        0.6 * inch,
        0.6 * inch,
        0.6 * inch,
        0.3 * inch,
        0.85 * inch,
        0 * inch,
    ]
    col_widths[-1] = (letter[0] - 2 * inch) - sum(col_widths[:-1])

    table = Table(full_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(style)
    elements.append(table)

    elements.append(Spacer(0, 20))

    return elements


def create_dimension_details(parser: StackParser, info):
    elements = []
    image_search_path = get_absolute_path(
        info["SAVE_FILE"], info[OptionsWidget.IMAGE_FOLDER]
    )
    max_width = float(info[OptionsWidget.MAX_IMG_WIDTH]) * inch
    max_height = float(info[OptionsWidget.MAX_IMG_HEIGHT]) * inch

    # Identify all unique PNs and associated dimensions
    PNs = defaultdict(set)
    for key, dim in parser.dimensions.items():
        if dim.PN:
            PNs[dim.PN].add(key)

    # iterate over PNs in alphabetical order, case-insensitive
    for PN in sorted(PNs, key=lambda x: x.lower()):
        # Section title
        elements.append(
            Paragraph(f"PART NUMBER {PN}:", PDFStyles["SectionHeaderStyle"])
        )

        # Add image if it exists
        image = find_image(image_search_path, PN, max_width, max_height)
        if image is not None:
            append_or_extend(elements, image)
        else:
            pass
            # TODO: determine if we want to flag missing images.
            # elements.append(
            #     Paragraph(f"Warning, no image found in {image_search_path} for '{expr.key}'")
            # )

        # Dimension Summary Table
        headers = [["ID", "Nom.", "+", "-", "D", "Note"]]
        data = []
        style = TableStyle(
            [
                ("ALIGN", (0, 0), (4, -1), "RIGHT"),
                ("ALIGN", (4, 0), (4, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("VALIGN", (0, 1), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (4, -1), 2),
                ("RIGHTPADDING", (0, 0), (4, -1), 2),
            ]
        )

        for dkey in sorted(PNs[PN]):
            D = parser.dimensions[dkey]
            row = [
                D.key,
                format_shortest(D.nom, 4),
                format_shortest(D.plus, 3),
                format_shortest(D.minus, 3),
                get_code_from_dist(D.disttype),
                Paragraph(D.note if D.note else "", PDFStyles["PlainStyle"]),
            ]
            data.append(row)

            if info[OptionsWidget.WHERE_USED] and D.key in parser.where_used:
                usagetext = f"Used in: {', '.join([f'{expr_key}' for expr_key in sorted(parser.where_used[D.key])])}"
                data.append(
                    [
                        "",
                        "",
                        "",
                        "",
                        "",
                        Paragraph(usagetext, PDFStyles["PlainStyle"]),
                    ]
                )
                style.add("BOTTOMPADDING", (0, len(data) - 1), (-1, len(data) - 1), 0)
                style.add("BOTTOMPADDING", (0, len(data)), (-1, len(data)), 5)
                style.add("NOSPLIT", (0, len(data) - 1), (-1, len(data)))

        full_data = headers + data

        col_widths = [
            0.5 * inch,
            0.6 * inch,
            0.6 * inch,
            0.6 * inch,
            0.3 * inch,
            0 * inch,
        ]
        col_widths[-1] = (letter[0] - 2 * inch) - sum(col_widths[:-1])

        table = Table(full_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(style)
        elements.append(table)

    return elements


def create_expression_summary(parser: StackParser, info):
    elements = []

    # Section title
    elements.append(Paragraph("EXPRESSION SUMMARY:", PDFStyles["SectionHeaderStyle"]))

    # Dimension Summary Table
    headers = [["ID", "Note"]]
    data = []
    style = TableStyle(
        [
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("VALIGN", (0, 1), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (0, -1), 2),
            ("RIGHTPADDING", (0, 0), (0, -1), 2),
            ("LEFTPADDING", (1, 0), (-1, -1), 10),
        ]
    )

    for E in parser.expressions.values():
        row = [
            E.key,
            Paragraph(E.note if E.note else "", PDFStyles["PlainStyle"]),
        ]
        data.append(row)

    full_data = headers + data

    col_widths = [0.5 * inch, 0 * inch]
    col_widths[-1] = (letter[0] - 2 * inch) - sum(col_widths[:-1])

    table = Table(full_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(style)
    elements.append(table)

    elements.append(Spacer(0, 20))

    return elements


def create_expression_details(parser: StackParser, info):
    elements = []

    for E in parser.expressions.values():
        append_or_extend(elements, create_single_expression(E, info))

    return elements


def create_single_expression(expr: StackExpr, info):
    elements = []
    value = expr.evaluate()
    image_search_path = get_absolute_path(
        info["SAVE_FILE"], info[OptionsWidget.IMAGE_FOLDER]
    )
    max_width = float(info[OptionsWidget.MAX_IMG_WIDTH]) * inch
    max_height = float(info[OptionsWidget.MAX_IMG_HEIGHT]) * inch

    # TODO: figure out a way to split short descriptions and long notes. Extra data column?

    title = Paragraph(
        f"<b>{expr.key}:</b> {expr.note}", PDFStyles["SectionHeaderStyle"]
    )
    elements.append(title)

    # Add image if it exists and image inclusion is enabled
    if info[OptionsWidget.FIND_IMAGES]:
        images = find_image(image_search_path, expr.key, max_width, max_height)
        if images is not None:
            append_or_extend(elements, images)
        else:
            pass
            # TODO: determine if we want to flag missing images.
            # elements.append(
            #     Paragraph(f"Warning, no image found in {image_search_path} for '{expr.key}'")
            # )

    expression = Paragraph(f"{expr.expr}", PDFStyles["PlainStyle"])
    expansion = Paragraph(f"{expr.expand()}", PDFStyles["PlainStyle"])
    evaluation = Paragraph(f"{expr.method}", PDFStyles["PlainStyle"])
    nominal = Paragraph(f"{format_shortest(value.nom,3)}")

    value_table = create_tolerance_table(expr, value)

    lb_table = create_bound_table(expr, value, lower=True)
    ub_table = create_bound_table(expr, value, lower=False)

    if info[OptionsWidget.SHOW_PLOTS]:
        graph = generate_dist_plot(
            expr,
            value=value,
            width=3 * inch,
            height=1 * inch,
            axis_font_size=10,
            line_weight=5,
            dpi=300,
            spine_linewidth=2,
        )
    else:
        graph = Paragraph("", PDFStyles["PlainStyle"])

    top_table = [
        ["Expression:", expression, graph],
        ["Expansion:", expansion, ""],
        ["Eval. Method:", evaluation, ""],
        ["Nominal:", nominal, ""],
        ["Value:", value_table, ""],
        ["Lower:", lb_table, ""],
        ["Upper:", ub_table, ""],
    ]
    style = TableStyle(
        [
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (1, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (0, -1), 24),  # Expression info indent
            ("SPAN", (2, 0), (2, -1)),  # Image span
            ("VALIGN", (2, 0), (2, -1), "CENTER"),  # Image alignment
            ("VALIGN", (1, 4), (1, 4), "CENTER"),  # tolerance alignment
            ("LEFTPADDING", (0, 5), (0, -1), 36),  # Bound info indent
        ]
    )
    col_widths = [1.3 * inch, 2 * inch, 0 * inch]
    col_widths[-1] = (letter[0] - 2 * inch) - sum(col_widths[:-1])
    row_heights = []
    for row in top_table:
        _, h = row[1].wrap(col_widths[1], letter[1])
        row_heights.append(h)
    row_heights[2] += 5  # space after expression info
    # row_heights[-1] = 1 * inch - sum(row_heights[:-1])

    table = Table(top_table, colWidths=col_widths, rowHeights=row_heights)
    table.setStyle(style)
    elements.append(table)

    expr_group = KeepTogether(elements)

    output = [expr_group]

    if info[OptionsWidget.SENSITIVITY]:
        s = expr.sensitivities()
        append_or_extend(output, create_sensitivity_table(expr, s))

    if info[OptionsWidget.CONTRIBUTIONS]:
        c = expr.contributions()
        append_or_extend(output, create_contribution_table(expr, c))

    return output


def create_tolerance_table(expr: StackExpr, value: StackDim) -> Table:
    center_text = f"{format_shortest(value.center(expr.method),3)}"
    plus_text = f"{format_shortest(value.upper_tol(expr.method),2)}"
    minus_text = f"{format_shortest(value.lower_tol(expr.method),2)}"

    center = Paragraph(center_text, PDFStyles["PlainStyle"])
    plus = Paragraph(
        plus_text,
        PDFStyles["ToleranceStyle"],
    )
    minus = Paragraph(
        minus_text,
        PDFStyles["ToleranceStyle"],
    )

    data = [[center, plus, ""], ["", minus, ""]]
    style = TableStyle(
        [
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (1, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (0, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("SPAN", (0, 0), (0, -1)),  # center span
            # ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )

    center_width = pdfmetrics.stringWidth(
        center_text, PDFStyles["PlainStyle"].fontName, PDFStyles["PlainStyle"].fontSize
    )
    dim_width = max(
        pdfmetrics.stringWidth(
            plus_text,
            PDFStyles["ToleranceStyle"].fontName,
            PDFStyles["ToleranceStyle"].fontSize,
        ),
        pdfmetrics.stringWidth(
            minus_text,
            PDFStyles["ToleranceStyle"].fontName,
            PDFStyles["ToleranceStyle"].fontSize,
        ),
    )
    col_widths = [center_width + 4, dim_width + 1, "*"]
    row_heights = [PDFStyles["ToleranceStyle"].fontSize] * 2

    table = Table(data, colWidths=col_widths, rowHeights=row_heights)
    table.setStyle(style)
    return table


def create_bound_table(expr: StackExpr, value: StackDim, lower=True) -> Table:
    bound = expr.lower if lower else expr.upper
    actual = value.lower(expr.method) if lower else value.upper(expr.method)
    meet_req = bound <= actual if lower else actual <= bound
    if isclose(bound, actual, abs_tol=1e-9):
        meet_req = True

    text1 = "NONE" if isinf(bound) else f"{format_shortest(bound,4)}"
    para1 = Paragraph(
        text1,
        PDFStyles["PlainStyle"],
    )

    text2 = (
        '<font color="#009E73"><b>PASS</b></font>'
        if meet_req
        else f'<font color="#D55E00"><b>FAIL:</b></font> {format_shortest(actual,4)}'
    )
    para2 = Paragraph(
        text2,
        PDFStyles["PlainStyle"],
    )

    data = [[para1, para2]]
    style = TableStyle(
        [
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (1, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
        ]
    )
    col_widths = [0.725 * inch, "*"]

    table = Table(data, colWidths=col_widths)
    table.setStyle(style)
    return table


def create_sensitivity_table(E: StackExpr, sensitivities):
    elements = []

    elements.append(Spacer(0, 3))
    elements.append(Paragraph("Sensitivities:", PDFStyles["ExpressionSubheadStyle"]))

    scale = max(abs(val) for val in sensitivities.values())

    # avoid division by zero in format
    # If scale is zero then all items are near zero so scale doesn't matter.
    if isclose(scale, 0, abs_tol=1e-9):
        scale = 1

    data = []
    for var, partial in sensitivities.items():
        data.append(
            [
                f"∂/∂{var}:",
                f"{format_shortest(partial,2)}",
                generate_center_bar_image(partial / scale, 1 * inch, 12),
            ]
        )
    style = TableStyle(
        [
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("VALIGN", (2, 0), (2, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (0, -1), 30),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            # ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]
    )
    col_widths = [1.05 * inch, 0.5 * inch, "*"]
    table = Table(data, colWidths=col_widths)
    table.setStyle(style)
    elements.append(table)

    return KeepTogether(elements)


def create_contribution_table(E: StackExpr, contributions):
    elements = []

    elements.append(Spacer(0, 3))
    elements.append(Paragraph("Contributions:", PDFStyles["ExpressionSubheadStyle"]))

    scale = max(abs(val) for val in contributions.values())

    # avoid division by zero in format
    # If scale is zero then all items are near zero so scale doesn't matter.
    if isclose(scale, 0, abs_tol=1e-9):
        scale = 1

    data = []
    for var, tol in contributions.items():
        data.append(
            [
                f"{var}:",
                f"±{format_shortest(tol,2)[1:]}",
                generate_bar_image(tol / scale, 1 * inch, 12),
            ]
        )
    style = TableStyle(
        [
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("VALIGN", (2, 0), (2, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (0, -1), 30),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            # ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]
    )
    col_widths = [1.05 * inch, 0.5 * inch, "*"]
    table = Table(data, colWidths=col_widths)
    table.setStyle(style)
    elements.append(table)

    return KeepTogether(elements)


# Helper function to convert a plot into an image suitable for ReportLab
def generate_dist_plot(
    expr: StackExpr,
    value: StackDim = None,
    width=3 * inch,
    height=1 * inch,
    axis_font_size=10,
    dpi=300,
    line_weight=1,
    spine_linewidth=1,
) -> Image:
    pixel_scale = dpi / inch

    # Extracting data for points and statistical lines
    if value is None:
        value = expr.evaluate()

    points = value.dist().flatten()
    l = value.lower(method=expr.method)
    lb = expr.lower
    m = value.center(method=expr.method)
    ub = expr.upper
    u = value.upper(method=expr.method)

    # Creating the plot with specified dimensions and font sizes
    fig, ax = plt.subplots(
        figsize=((width / inch) * pixel_scale, (height / inch) * pixel_scale), dpi=dpi
    )
    ax.hist(points, bins=71, color="lightgrey", edgecolor="none")

    # Drawing vertical lines at specified points with adjustable line weight
    ax.axvline(l, color="black", linestyle="--", linewidth=line_weight)
    ax.axvline(m, color="black", linestyle="-", linewidth=line_weight)
    ax.axvline(u, color="black", linestyle="--", linewidth=line_weight)

    # Adjust the thickness of the lines surrounding the plot area
    for spine in ax.spines.values():
        spine.set_linewidth(spine_linewidth)

    if not isinf(expr.lower):
        lb_color = "#D55E00" if lb > l else "#009E73"

        ax.axvline(
            lb,
            color=lb_color,
            linestyle="--",
            linewidth=line_weight,
        )
        ymax = ax.get_ylim()[1]
        ax.text(
            lb,
            ymax,
            "LB",
            color=lb_color,
            fontsize=axis_font_size * pixel_scale,
            ha="right",
            va="bottom",
        )

    if not isinf(expr.upper):
        ub_color = "#D55E00" if ub < u else "#009E73"

        ax.axvline(
            ub,
            color=ub_color,
            linestyle="--",
            linewidth=line_weight,
        )
        ymax = ax.get_ylim()[1]
        ax.text(
            ub,
            ymax,
            "UB",
            color=ub_color,
            fontsize=axis_font_size * pixel_scale,
            ha="left",
            va="bottom",
        )

    # Remove y-axis label and tick marks
    ax.set_yticks([])
    ax.set_ylabel("")

    # Display only 3 x tick marks and remove x label
    ax.set_xticks(
        [
            ax.get_xticks()[0],
            (ax.get_xticks()[0] + ax.get_xticks()[-1]) / 2,
            ax.get_xticks()[-1],
        ]
    )
    ax.set_xlabel("")

    # Setting the font sizes for the ticks
    ax.tick_params(axis="x", labelsize=axis_font_size * pixel_scale)

    # Labeling the vertical lines

    # Adjust layout to ensure the labels are not cut off
    # TODO: See if subplots_adjust allows all the plots to render at the same size
    plt.tight_layout(pad=1.5)

    # Saving the plot to a BytesIO buffer with higher DPI for better quality
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=dpi)
    plt.close(fig)

    buf.seek(0)
    graph = Image(buf, width=width, height=height)

    return graph


def generate_center_bar_image(val, width=3 * inch, height=1 * inch, dpi=300):
    # Check if val is within the range [-1, 1]
    if not -1 <= val <= 1:
        raise ValueError("The value must be in the range [-1, 1]")

    # Creating the plot with specified dimensions and DPI
    pixel_scale = dpi / inch
    fig, ax = plt.subplots(
        figsize=(width / inch * pixel_scale, height / inch * pixel_scale), dpi=dpi
    )

    # Set all spines to be invisible
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Plotting vertical lines
    ax.axvline(-1, color="black", linestyle="-", linewidth=0.75 * pixel_scale)
    ax.axvline(0, color="black", linestyle="-", linewidth=1.5 * pixel_scale)
    ax.axvline(1, color="black", linestyle="-", linewidth=0.75 * pixel_scale)

    # Draw the bar using axhspan
    left = min(0, val)
    right = max(0, val)
    plt.fill((left, right, right, left), (0.15, 0.15, 0.85, 0.85), "#56B4E9", alpha=0.5)
    #     0.15,
    #     0.85,
    #     xmin=left,
    #     xmax=right,
    #     color="green",
    #     alpha=0.5,
    #     linewidth=None,
    # )

    # Remove x and y axis labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylim((0, 1))

    # Adjust layout to ensure the plot looks nice
    plt.tight_layout()

    # Saving the plot to a BytesIO buffer
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=dpi)
    plt.close(fig)
    buf.seek(0)

    bar = Image(buf, width=width, height=height)
    return bar


def generate_bar_image(val, width=3 * inch, height=1 * inch, dpi=300):
    # Check if val is within the range [0, 1]
    if not 0 <= val <= 1:
        raise ValueError("The value must be in the range [0, 1]")

    # Creating the plot with specified dimensions and DPI
    pixel_scale = dpi / inch
    fig, ax = plt.subplots(
        figsize=(width / inch * pixel_scale, height / inch * pixel_scale), dpi=dpi
    )

    # Set all spines to be invisible
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Plotting vertical lines
    ax.axvline(0, color="black", linestyle="-", linewidth=0.75 * pixel_scale)
    ax.axvline(1, color="black", linestyle="-", linewidth=0.75 * pixel_scale)

    # Draw the bar using axhspan
    left = 0
    right = val
    plt.fill((left, right, right, left), (0.15, 0.15, 0.85, 0.85), "#56B4E9", alpha=0.5)

    # Remove x and y axis labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylim((0, 1))

    # Adjust layout to ensure the plot looks nice
    plt.tight_layout()

    # Saving the plot to a BytesIO buffer
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=dpi)
    plt.close(fig)
    buf.seek(0)

    bar = Image(buf, width=width, height=height)
    return bar


# Helper function to create flowables from a data object
def create_flowables(data_object, include_graphs=False, include_images=False):
    styles = getSampleStyleSheet()

    # Paragraph content
    paragraph_content = [
        Paragraph(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            styles["BodyText"],
        ),
        Paragraph(
            "Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae;",
            styles["BodyText"],
        ),
    ]

    if include_graphs:
        aspect_ratio = 4
        height = 0.67
        dpi = 300

        graph_image = generate_dist_plot(
            data_object,
            width=height * aspect_ratio * dpi,
            height=height * dpi,
            axis_font_size=20,
            line_weight=5,
            dpi=dpi,
            spine_linewidth=2,
        )

        graph = Image(
            graph_image, width=height * aspect_ratio * inch, height=height * inch
        )

        # Create table with paragraphs on the left and the image on the right
        table_data = [[paragraph_content[0], graph]]
        col_widths = [None, height * aspect_ratio * inch]
        table = Table(table_data, colWidths=col_widths)

        # Add table style to control alignment and spacing
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (0, 0), 0),
                    ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ]
            )
        )

        flowables = [table]
    else:
        flowables = paragraph_content[
            :1
        ]  # if no graph included, keep only the first paragraph

    flowables.append(Spacer(1, 12))
    flowables.append(paragraph_content[1])  # always add the second paragraph

    if include_images:
        pass  # do image lookup stuff here

    return flowables


# Helper function to get the lowest level folder containing a file
def get_lowest_level_folder(filename):
    path = Path(filename).resolve()
    return path.parent


# Helper function to search for a .png file and return the image data
def find_image(folder, name, max_width, max_height):
    # Define possible image extensions
    extensions = ["jpg", "jpeg", "png", "gif", "bmp", "tiff"]

    images = []

    def get_target_size(orig_w, orig_h, max_w, max_h):
        orig_ar = orig_h / orig_w
        max_ar = max_h / max_w

        if orig_ar > max_ar:
            new_h = max_h
            new_w = int(max_h / orig_ar)

        else:
            new_w = max_w
            new_h = int(max_w * orig_ar)

        return (new_w, new_h)

    def load_image(file_path):
        # Open the image using PIL to get dimensions
        pil_image = PILImage.open(file_path)
        original_width, original_height = pil_image.size

        # Calculate new height to maintain aspect ratio
        new_width, new_height = get_target_size(
            original_width, original_height, max_width, max_height
        )

        # Create and return the scaled Image object from reportlab
        images.append(Image(file_path, width=new_width, height=new_height))

    # Search for the base image without suffix
    for ext in extensions:
        file_path = os.path.join(folder, f"{name}.{ext}")
        if os.path.isfile(file_path):
            load_image(file_path)
            break  # only grab the first base image found

    # Search for alpha-suffixed images (namea.ext, nameb.ext, etc.)
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for letter in alphabet:
        found_letter = False
        for ext in extensions:
            suffixed_file_path = os.path.join(folder, f"{name}{letter}.{ext}")
            if os.path.isfile(suffixed_file_path):
                load_image(suffixed_file_path)
                found_letter = True
                break  # only grab first image with this suffix
        if not found_letter:
            break  # stop looking for further suffixes if one is not found

    # Return None if no image file is found
    return None if not images else images


def append_or_extend(lst, item):
    if isinstance(item, Iterable) and not isinstance(
        item, str
    ):  # strings are iterable but should be treated as single items
        lst.extend(item)
    else:
        lst.append(item)


# Example usage
if __name__ == "__main__":
    input_filename = "validation_inputs/test_input_v3.txt"
    output_filename = "test_outputs/example_report.pdf"

    info = open_from_name(input_filename)
    info[OptionsWidget.FIND_IMAGES] = True
    info[OptionsWidget.WHERE_USED] = True
    info[OptionsWidget.SENSITIVITY] = True

    info["SAVE_FILE"] = os.path.abspath(input_filename)

    SP = StackParser()
    SP.parse(
        constants_data=info[DataWidget.CONSTANTS],
        dimensions_data=info[DataWidget.DIMENSIONS],
        expressions_data=info[DataWidget.EXPRESSIONS],
    )

    format_pdf(output_filename, SP, info)
