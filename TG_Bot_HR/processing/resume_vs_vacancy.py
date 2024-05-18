import json
import re
import os
from settings import settings
from openai import AsyncOpenAI
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


directories = [settings.resumes_json_files,
               settings.vacancies_json_files,
               settings.pdf_report_files]
for dir in directories:
    os.makedirs(dir, exist_ok=True)

RESUMES_JSON_FILES = directories[0]
VACANCIES_JSON_FILES = directories[1]
PDF_REPORT_FILES = directories[2]

os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()
current_date = f"{datetime.now().strftime('%Y-%m')}-01"
system = "Ты профессиональный HR."

def question_skills(resume_skills, vacancy_skills):
    return re.sub(r'\s+', ' ', f"""
    *** You have the position and skills of a candidate from a resume: {resume_skills}. ***
    *** You also have the necessary position and skills listed in the vacancy: {vacancy_skills}. ***    
    Compare the skills of the candidate in the resume and the requirements from the vacancy.    
    * Questions #1: Specify which skills from the RESUME match the skills in the vacancy.
    * Questions #2: Specify which skills are listed on the resume, but not listed in the vacancy.
    * Questions #3: Specify which skills are missing from the resume compared to the required skills 
      from the vacancy.    
    * Questions #4: What is the percentage from 0 to 100 of matching skills in the candidate's resume 
      compared to the necessary skills in the vacancy and why? Answer the question briefly in one sentence. 
      Отвечай на русском языке. Если слова - навыки указаны на английском - выводи навыки на английском.
      В каждый ответ включи саммари вопроса, на который получен ответ. Выдавай только саммари вопроса и ответ.
      После каждого ответа ставь перенос строки: <br/>. При форматировании текста используй HTML теги: 
      <b>Жирный текст</b>, <i>курсив</i>, <u>подчеркивание</u> и другие стили, а также перенос строки <br/>""")


def main_skill(resume_skills, resume_experience, current_date=current_date):
    return re.sub(r'\s+', ' ', f"""
    *** You have the position and skills of a candidate from a resume: {resume_skills}. *** 
    *** You have the experience of a candidate from a resume: {resume_experience}. *** 
    Определи, какой один навык (skill) является самым важным и основным навыком для указанной позиции.
    После этого, Пожалуйста, посчитай сумму месяцев временных интервалов работы по основному навыку 
    на основании опыта кандидата, если этот основной навык упомянут в этом интервале.    
    Необходимо учитывать все интервалы работы, где упоминается основной навык.
    Если в интервале работы НЕТ упоминания основного навыка - этот интервал не считать.
    Какой суммарный опыт в месяцах по основному навыку ? Выведи расчет и количество месяцев.
    Даты в резюме указаны в формате: yyyy-mm-dd. Если дата "to None" - используй {current_date}.""")


async def resume_parsing(resume_json):
    if resume_json.endswith('.json'):
        with open(resume_json, 'r', encoding='utf-8') as r:
            resume = json.load(r)
        resume_dict = dict()
        # ****************************************************
        resume_dict['position_skills'] = re.sub(r'\s+', ' ', f"""
                     Position: {resume['title']} .
                     Skills: {(', ').join(resume['skill_set'])}""")

        if resume['skills'] != None: # Add.skills
            add_skills = f"{resume['skills']}."
        else:
            add_skills = ''
        resume_dict['add_skills'] = add_skills

        experience = ''
        for n, place in enumerate(resume['experience']):
            experience += f""" *** Job experience {n+1}: 
                          Position - {place['position']}.
                          Period (yyyy-mm-dd): from {place['start']} to {place['end']}. 
                          Description of job {n+1}: {place['description']} """
        resume_dict['experience'] = re.sub(r'\s+', ' ', f'{experience}')
        return resume_dict


async def vacancy_parsing(vacancy_json):
    if vacancy_json.endswith('.json'):
        with open(vacancy_json, 'r', encoding='utf-8') as r:
            vacancy = json.load(r)
        vacancy_dict = dict()
        # **************************************************************************************************
        vacancy_dict['position_skills'] = re.sub(r'\s+', ' ', f"""
                                          Position: {vacancy['data'].get('position', '')}. 
                                          Skills: {(', ').join(vacancy['data'].get('skills', ''))}. """)
        vacancy_dict['mandatory_requirements'] = re.sub(r'\s+', ' ', f"""
                      Requirements: {(' ').join(vacancy['data'].get('mandatoryRequirements', ''))} """)
        vacancy_dict['additional_requirements'] = re.sub(r'\s+', ' ', f"""
                          Add.Requirements: {(' ').join(vacancy['data'].get('additionalRequirements', ''))} """)
        vacancy_dict['levels'] = f"Levels: {(', ').join(vacancy['data'].get('experienceLevels', ''))}. "
        vacancy_dict['tasks'] = \
                    re.sub(r'\s+', ' ', f"Tasks: {(' ').join(vacancy['data'].get('projectTasks'))} ")
        return vacancy_dict


async def answer_gpt(messages, temp=0):
    completion = await AsyncOpenAI().chat.completions.create(
                                     model="gpt-3.5-turbo-0125",
                                     messages=messages,
                                     temperature=temp)
    return completion.choices[0].message.content


async def get_answers_gpt(resume_dict, vacancy_dict):
    answers_gpt = dict()
    # Сравнение Скилов ****************************************************
    content_1 = question_skills(resume_dict['position_skills'],
                                vacancy_dict['position_skills'] + vacancy_dict['mandatory_requirements'])
    message_1 = [{"role": "system", "content": system},
                 {"role": "user", "content": f"{content_1}"}]
    answers_gpt['all_skills'] = await answer_gpt(message_1, temp=0)
    # Определение основного Скилла и опыта *********************************
    content_2 = main_skill(resume_dict['position_skills'],
                           resume_dict['experience'])
    message_2 = [{"role": "system", "content": system},
                 {"role": "user", "content": f"{content_2}"}]
    answers_gpt['main_skill'] = await answer_gpt(message_2, temp=0)
    # ******************************************
    return answers_gpt


async def create_pdf(pdf_file_path, paragraphs):
    pdfmetrics.registerFont(TTFont('TimesNewRoman', 'data/TimesNewRoman.ttf'))
    doc = SimpleDocTemplate(pdf_file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    style = styles["BodyText"]
    style.fontName = "TimesNewRoman"
    style.fontSize = 14
    style.leading = 14
    story = []
    for paragraph in paragraphs:
        story.append(Paragraph(paragraph, style))
        story.append(Spacer(1, 14))
    doc.build(story)


async def main_vs(resume_json, vacancy_json):
    resume_dict = await resume_parsing(resume_json)
    vacancy_dict = await vacancy_parsing(vacancy_json)
    answers_gpt = await get_answers_gpt(resume_dict, vacancy_dict)
    try:  # PDF отчет. ************************************************
        pdf_file_name = f"{resume_json[8:-5]}_+_{vacancy_json[8:-5]}.pdf"
        path = os.path.join(f'{PDF_REPORT_FILES}', pdf_file_name)
        paragraphs = [f"Резюме: {resume_json[8:]}",
                      f"Вакансия: {vacancy_json[8:]}",
                      f"{answers_gpt['all_skills']}",
                      f"{answers_gpt['main_skill']}"]
        await create_pdf(path, paragraphs)
        return path
    except Exception as ex:
        print('PDF отчет:', ex)
