import re


system_0 = re.sub(r'\s+', ' ', """You are a professional HR. You help candidates to get 
           a job for the chosen vacancy""")

assistant_0 = "['missing skill 1', 'missing skill 2', 'missing skill 3', ...]"

assistant_1 = f"""
#1: ...
#2: ...
#3: *** Резюме: ... *** Вакансия: ...
"""

def question_00(resume_skills, vacancy_skills):
    return re.sub(r'\s+', ' ', f"""
    *** You have the skills of a candidate from a resume: {resume_skills}. ***
    *** You also have the necessary skills listed in the vacancy: {vacancy_skills}. ***
    Questions: Give me a list (in the form of a Python list), what skills does a candidate 
    lack in a resume compared to the necessary skills in a vacancy? Please answer the 
    question briefly, just list the candidate's missing skills (as a list in Python).""")

def message_content_01(resume, vacancy):
    return re.sub(r'\s+', ' ', f"""
    You have a candidate's resume: {resume}. ***
    You also have a selected vacancy: {vacancy}. ***
    Analyze the information from the candidate's resume and the requirements from the vacancy. 
    Answer all questions in Russian, with the exception of the words denoting the candidate's 
    skills, if you write about them. So, answer in Russian, but if you use words denoting the 
    candidate's skills, write skills in English.""")

def question_01(resume_skills, vacancy_skills):
    return re.sub(r'\s+', ' ', f"""
    *** You have the skills of a candidate from a resume: {resume_skills}. ***
    *** You also have the necessary skills listed in the vacancy: {vacancy_skills}. ***
    Questions #1: What is the percentage from 0 to 100 of matching skills in the candidate's resume compared
    to the necessary skills in the vacancy? Answer the question briefly in one sentence in Russian.""")

def question_02(resume_part=None, vacancy_part=None):
    return re.sub(r'\s+', ' ', f""" * Questions #2:
    What can be said about the candidate's other competencies (except skills) in comparison with 
    the requirements of the vacancy (except skills)? Answer in Russian.""")

def question_03(resume_part=None, vacancy_part=None):
    return re.sub(r'\s+', ' ', f""" * Questions #3:
    Sammarize the fields of the resume: Salary, Languages, Job schedule, Location, Attitude to relocation. *
    AND Sammarize vacancy fields: Salary, Levels, Work Format, Required Location. * Answer in Russian.""")
