from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def create_pdf(pdf_filename, paragraphs):
    pdfmetrics.registerFont(TTFont('TimesNewRoman', 'data/TimesNewRoman.ttf'))
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    styles = getSampleStyleSheet()
    style = styles["BodyText"]
    style.fontName = "TimesNewRoman"
    style.fontSize = 14
    style.leading = 14
    story = []
    for paragraph in paragraphs:
        story.append(Paragraph(paragraph, style))
        story.append(Spacer(1, 14))  # Добавляем пробел после каждого абзаца
    doc.build(story)
