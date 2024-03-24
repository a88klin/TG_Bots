import re


def system_01():
    return re.sub(r'\s+', ' ', """You are a professional HR.
    You help candidates (applicants) to get a job for the chosen vacancy""")

def message_content_01(resume, vacancy):
    return re.sub(r'\s+', ' ', f"""Based on the candidate's resume, you have found a suitable vacancy.
    Candidate's desired position, candidate's skills, additional information about the candidate
    from the resume: {resume}. Requirements for the candidate, according
    to the vacancy you have chosen: {vacancy}. Analyze the information from the candidate's
    resume and the requirements from the vacancy.""")

def assistant_01():
    pass

def question_01(r2, v2):
    return re.sub(r'\s+', ' ', f"""Answer the questions:
    1. What is the percentage from 0 to 100 of matching skills in the candidate's resume compared
       to the necessary skills in the vacancy? 
    2. What skills and competencies does the candidate lack in the resume compared to the necessary
       skills and competencies in the vacancy?
    3. Compare and give a conclusion about the compliance and differences in the resume part: {r2}
       and the vacancy part: {v2}. Compare only what is logical to compare.

    Answer all questions in Russian, with the exception of the words denoting the candidate's skills,
    if you write about them. So, answer in Russian, but if you use words denoting the candidate's skills,
    write skills in English.""")
