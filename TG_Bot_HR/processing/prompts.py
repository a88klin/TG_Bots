from datetime import datetime
import re


system = re.sub(r'\s+', ' ', """You are a professional HR. You help candidates to get 
                                a job for the chosen vacancy""")

assistant_0 = "['group of missing skills 1', 'group of missing skill 2', ... , 'group of missing skill 5']"

def question_skills(resume_skills, vacancy_skills_and_requirements):
    return re.sub(r'\s+', ' ', f"""
    *** You have the skills of a candidate from a resume: {resume_skills}. ***
    *** You also have the necessary skills listed in the vacancy: {vacancy_skills_and_requirements}. ***
    
    Compare the skills of the candidate in the resume and the requirements from the vacancy.
    
    Any combination of SQL in the resume words and any combination of SQL in the vacancy 
    requirements means that the candidate has the skill for any combination of SQL except NoSQL.
    
    Give me a report on the 5 most important missing skills on your resume (in the form of a 
    Python list), based on the requirements from the vacancy.
    
    The missing skills should be grouped by meanings and areas of activity and sorted by 
    importance (in the form of a Python list).
    
    Отвечай на русском языке. Если слова - навыки указаны на английском - выводи навыки на английском.""")

def question_skills_2(resume_skills, vacancy_skills_and_requirements):
    return re.sub(r'\s+', ' ', f"""
    *** You have the skills of a candidate from a resume: {resume_skills}. ***
    *** You also have the necessary skills listed in the vacancy: {vacancy_skills_and_requirements}. ***
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

def question_skills_3(resume_skills, vacancy_skills_and_requirements):
    return re.sub(r'\s+', ' ', f"""
    *** You have the position and skills of a candidate from a resume: {resume_skills}. ***
    *** You also have the necessary position and skills listed in the vacancy: {vacancy_skills_and_requirements}. ***  
      
    Compare the skills of the candidate in the resume and the requirements from the vacancy. 
         
    * Questions #1: Specify which skills from the RESUME match the skills in the vacancy.
    * Questions #2: Specify which skills are listed on the resume, but not listed in the vacancy.
    * Questions #3: Specify which skills are missing from the resume compared to the required skills 
      from the vacancy. 
    * Questions #4: What is the percentage from 0 to 100 of matching skills in the candidate's resume 
      compared to the necessary skills in the vacancy and why? Answer the question briefly in one sentence.
    * Questions #5: What can be said about the candidate's other competencies (except skills) in comparison 
      with the requirements of the vacancy (except skills)? Answer in Russian. 
    * Questions #6: Sammarize the fields of the Resume: Salary, Languages, Job schedule, Location, 
      Attitude to relocation. * AND Sammarize vacancy fields: Salary rate, Levels, Work Format, Required Location. 
      Answer in Russian. Insert a line break <br/> between the Resume and Vacancy answers. 
    
    *** Отвечай на русском языке. Если слова - навыки указаны на английском - выводи навыки на английском.
      When displaying text, use HTML tags: <b>Bold text</b>, 
      <i>italics</i>, <u>underscores</u> and other styles, as well as line breaks <br/>.
      After answering each question, put a line break tag: <br/>""")


def main_skill(resume_skills, resume_experience):
    current_date = f"{datetime.now().strftime('%Y-%m')}-01"
    return re.sub(r'\s+', ' ', f"""
    *** You have the position and skills of a candidate from a resume: {resume_skills}. *** 
    *** You have the experience of a candidate from a resume: {resume_experience}. *** 
    Определи, какой один навык (skill) является самым важным и основным навыком для указанной позиции.
    После этого, Пожалуйста, посчитай сумму месяцев временных интервалов работы по основному навыку 
    на основании опыта кандидата, если этот основной навык упомянут в этом интервале.    
    Необходимо учитывать все интервалы работы, где упоминается основной навык.
    Если в интервале работы НЕТ упоминания основного навыка - этот интервал не считать.
    Какой суммарный опыт в месяцах по основному навыку ? Выведи расчет и количество месяцев.
    Даты в резюме указаны в формате: yyyy-mm-dd. Если дата "to None" - используй {current_date}.
    Каждый интервал суммируй один раз. Ответь на русском языке""")
