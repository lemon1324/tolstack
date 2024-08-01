from reportlab.lib.styles import ParagraphStyle

PDFStyles = {
    "TitleStyle": ParagraphStyle(
        name="TitleStyle",
        fontSize=24,
        leading=28,
        alignment=0,  # Left-aligned
        spaceAfter=5,
        textColor="black",
        fontName="Helvetica-Bold",
    ),
    "DocNoStyle": ParagraphStyle(
        name="DocNoStyle",
        fontSize=14,
        leading=16,
        alignment=0,  # Left-aligned
        spaceAfter=15,
        textColor="black",
        fontName="Helvetica",
    ),
    "PlainStyle": ParagraphStyle(
        name="PlainStyle",
        alignment=0,  # Left-aligned
        textColor="black",
    ),
    "ToleranceStyle": ParagraphStyle(
        name="ToleranceStyle",
        alignment=2,  # Right-aligned
        textColor="black",
        fontSize=7,
        leading=7,
    ),
    "BodyStyle": ParagraphStyle(
        name="BodyStyle",
        fontSize=12,
        leading=14,
        alignment=0,  # Left-aligned
        spaceAfter=2.5,
        textColor="black",
        fontName="Helvetica",
        firstLineIndent=12,
    ),
    "SectionHeaderStyle": ParagraphStyle(
        name="SectionHeaderStyle",
        fontSize=12,
        leading=14,
        alignment=0,  # Left-aligned
        leftIndent=0,
        spaceAfter=2.5,
        textColor="black",
        fontName="Helvetica-Bold",
    ),
    "ExpressionSubheadStyle": ParagraphStyle(
        name="ExpressionSubheadStyle",
        alignment=0,  # Left-aligned
        textColor="black",
        leftIndent=18,
    ),
    "HangingIndentStyle": ParagraphStyle(
        name="HangingIndentStyle",
        fontSize=10,
        leading=12,
        alignment=0,  # Left-aligned
        leftIndent=6,
        firstLineIndent=-6,
        textColor="black",
        fontName="Helvetica",
    ),
}


def update_paragraph_style(base_style: ParagraphStyle, **kwargs) -> ParagraphStyle:
    """
    Update the properties of a given ParagraphStyle based on keyword arguments.

    Parameters:
        base_style (ParagraphStyle): The style to be updated.
        kwargs: Keyword arguments representing the properties to be updated.

    Returns:
        ParagraphStyle: The updated ParagraphStyle.
    """
    for key, value in kwargs.items():
        if hasattr(base_style, key):
            setattr(base_style, key, value)
        else:
            raise AttributeError(f"ParagraphStyle has no attribute '{key}'")
    return base_style
