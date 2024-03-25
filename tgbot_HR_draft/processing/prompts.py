import re


def system_01():
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

def assistant_01():
    pass

def question_01():
    return re.sub(r'\s+', ' ', f""" Questions #1:
    What is the percentage from 0 to 100 of matching skills in the candidate's resume compared
    to the necessary skills in the vacancy? Please, answer is short in one sentence.""")

def question_02():
    return re.sub(r'\s+', ' ', f""" Questions #2:
    What SKILLS and competencies does the candidate lack in the resume compared to the necessary 
    SKILLS in the vacancy?""")

def question_03():
    return re.sub(r'\s+', ' ', f""" Questions #3:
    What can be said about the candidate's other competencies (except skills) in comparison with 
    the requirements of the vacancy (except skills)?""")

def question_04():
    return re.sub(r'\s+', ' ', f""" Questions #4:
    What can be said about the candidate's desired salary in the resume and salary in the vacancy?""")

def question_05():
    return re.sub(r'\s+', ' ', f""" Questions #5:
    Sammarize the fields of the resume: Languages, Job schedule, Location, Attitude to relocation. 
    AND Sammarize vacancy fields: Levels, Work Format, Required Location""")
