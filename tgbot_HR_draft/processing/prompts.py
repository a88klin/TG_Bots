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

def question_01(resume_part, vacansy_part):
    return re.sub(r'\s+', ' ', f"""Answer the questions:
    1. What is the percentage from 0 to 100 of matching skills in the candidate's resume compared
       to the necessary skills in the vacancy? Please, answer is short in one sentence. 
    2. What SKILLS and competencies does the candidate lack in the resume compared to the necessary
       SKILLS and competencies in the vacancy?
    3. Summarize and give a conclusion about the resume part: {resume_part} and the vacancy part: 
       {vacansy_part}. You can use a comparison, but compare only what is logical to compare.

    Answer all questions in Russian, with the exception of the words denoting the candidate's skills,
    if you write about them. So, answer in Russian, but if you use words denoting the candidate's skills,
    write skills in English.""")
