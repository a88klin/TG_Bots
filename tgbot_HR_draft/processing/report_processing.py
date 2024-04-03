from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from settings import settings
import os


PDF_REPORT_FILES = settings.pdf_report_files


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


async def report_pdf(resume_id, missing_skill_value_dict):
    missing_skill_value = ''
    for skill, value in missing_skill_value_dict.items():
        missing_skill_value += f'* {skill}:  {value}<br/>'
    try:
        paragraphs = [f"Резюме: {resume_id}",
                      f"Самооценка кандидата по владению навыками от 0 до 7:",
                      f"{missing_skill_value}"]
        pdf_file_name = f"{resume_id[:-5]}_-_missing_skills.pdf"
        path = os.path.join(f'{PDF_REPORT_FILES}', pdf_file_name)
        create_pdf(path, paragraphs)
    except Exception as ex:
        print('PDF отчет:', ex)
