import re


def system_01(text_part=None):
    return re.sub(r'\s+', ' ', """You are a professional HR. You help candidates (applicants) 
    to get a job for the chosen vacancy""")

def message_content_01(resume, vacancy):
    return re.sub(r'\s+', ' ', f"""
    You have a candidate's resume: {resume}. ***
    You also have a selected vacancy: {vacancy}. ***
    Analyze the information from the candidate's resume and the requirements from the vacancy. 
    Answer all questions in Russian, with the exception of the words denoting the candidate's 
    skills, if you write about them. So, answer in Russian, but if you use words denoting the 
    candidate's skills, write skills in English.""")

def question_01(resume_part=None, vacancy_part=None):
    return re.sub(r'\s+', ' ', f""" * Questions #1:
    What is the percentage from 0 to 100 of matching skills in the candidate's resume compared
    to the necessary skills in the vacancy? Please, answer is short in one sentence.""")

def question_02(resume_part=None, vacancy_part=None):
    return re.sub(r'\s+', ' ', f""" * Questions #2:
    If the candidate has any skill ...SQL in the resume, so he has the skill to meet the requirements 
    from vacancy for any ...SQL (for example, PostgreSQL, MS SQL and any other ...SQL) with the exception 
    of NoSQL. Therefore, consider that any mention of SQL in a resume and a vacancy is the same thing, 
    and the candidate has a skill in any SQL with the exception of NoSQL.
    What SKILLS and competencies does the candidate lack in the resume compared to the necessary 
    SKILLS in the vacancy?""")

def question_03(resume_part=None, vacancy_part=None):
    return re.sub(r'\s+', ' ', f""" * Questions #3:
    What can be said about the candidate's other competencies (except skills) in comparison with 
    the requirements of the vacancy (except skills)?""")

def question_04(resume_part=None, vacancy_part=None):
    return re.sub(r'\s+', ' ', f""" * Questions #4:
    What can be said about the candidate's desired salary in the resume and salary in the vacancy?""")

def question_05(resume_part=None, vacancy_part=None):
    return re.sub(r'\s+', ' ', f""" * Questions #5:
    Sammarize the fields of the resume: Languages, Job schedule, Location, Attitude to relocation. 
    AND Sammarize vacancy fields: Levels, Work Format, Required Location""")
