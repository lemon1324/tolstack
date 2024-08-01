from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Flowable, Paragraph


class TitleFlowable(Flowable):
    def __init__(self, title):
        Flowable.__init__(self)
        self.title = title

    def draw(self):
        style = ParagraphStyle(
            name="TitleStyle",
            fontSize=24,
            leading=28,
            alignment=0,  # Left-aligned
            spaceAfter=20,
            textColor="blue",
            fontName="Helvetica-Bold",
        )

        p = Paragraph(self.title, style)
        p.wrapOn(self.canv, self.width, self.height)
        p.drawOn(self.canv, 0, 0)

    def wrap(self, availWidth, availHeight):
        return availWidth, 36  # Height based on font size and leading
