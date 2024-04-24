from processing.start_mongodb import resumes_collection, vacancies_collection
from deep_translator import GoogleTranslator # pip install -U deep-translator
from settings import settings
import json
import os
import re


RESUMES_JSON_FILES = settings.resumes_json_files
os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()
transtator = GoogleTranslator(source='ru', target='en')
AMOUNT = 0


async def get_vacancy(_id):
    # Получаем Поля вакансии для сравнения и вопросов к ChatGPT **********************************************
    vacancy = await vacancies_collection.find_one({'_id': _id})
    vacancy_skills = vacancy['vacancy_skills']  # Only vacancy_skills
    chosen_vacancy = re.sub(r'\s+', ' ',
                            vacancy['position_skills_en'] +
                            vacancy['requirements1_en'] +
                            vacancy['requirements2_en'] +
                            vacancy['levels_en'] +
                            vacancy['salary_en'] +
                            vacancy['format_en'] +
                            vacancy['location_en'] +
                            vacancy['tasks_en'])
    return vacancy_skills, chosen_vacancy


def ids_and_scores(query, db_index, k=5):
    docs_and_scores = db_index.similarity_search_with_score(query, k=k)
    return [doc[1] for doc in docs_and_scores], \
           [f"{doc[0].metadata['file']}" for doc in docs_and_scores]


async def processing_resume_and_similarity_vacancies(resume_file_name, db_index, k=5):
    if not await resumes_collection.find_one({'_id': resume_file_name}): # если резюме нет в базе
        with open(os.path.join(f'{RESUMES_JSON_FILES}', resume_file_name), 'r', encoding='utf-8') as r:
            resume = json.load(r)
            resume['_id'] = resume_file_name  # Добавляю поле "_id" с именем файла

        schedules = '' # График работы
        for schedule in resume["schedules"]:
            schedules += f"{schedule['name']}, "

        experience = '' # Опыт
        for n, place in enumerate(resume['experience']):
            experience += f""" *** Job experience {n + 1}: 
                           Position - {place['position']}.
                           Period (yyyy-mm-dd): from {place['start']} to {place['end']}. 
                           Description of job {n + 1}: {place['description']} """

        languages = '' # Языки
        for lang in resume['language']:
            languages += f"{lang['name']} - {lang['level']['name']}. "

        try:
            currency = resume['salary']['currency']
            salary = f"Desired salary: {resume['salary']['amount']} \
                     {currency if currency!='RUR' else 'рублей в месяц'}. "
        except:
            salary = ''

        if resume['skills'] != None: # Add.skills
            add_skills = f"Add.skills: {resume['skills']}."
        else:
            add_skills = ''

        # Only skill_set from resume
        resume_skills = (', ').join(resume['skill_set'])
        #r1. Position, Skills, Add.Skills
        resume_line_1 = re.sub(r'\s+', ' ', f"""
                             Position: {resume['title']}. {resume['professional_roles'][0]['name']}.
                             Skills: {(', ').join(resume['skill_set'])}.
                             {add_skills}""")
        #r2. Salary, Languages, Job schedule, Location, Relocation, Total experience
        resume_line_2 = re.sub(r'\s+', ' ', f"""
                             {salary}
                             Languages: {languages}.
                             Job schedule: {schedules}.
                             Location: {resume['area']['name']}.
                             Attitude to relocation: {resume['relocation']['type']['name']}.
                             Total experience: {resume['total_experience']['months']} months. """)
        #r3. Experience (position + description)
        resume_line_3 = re.sub(r'\s+', ' ', f'{experience}')

        try: # сохраняю JSON и сформированные строки из полей резюме в коллекцию resumes
            await resumes_collection.insert_one(resume)
            await resumes_collection.find_one_and_update({'_id': resume['_id']}, # нахожу резюме по _id
                                                   {'$set': {'line_1': resume_line_1,    # Position, Skills, Add.skills
                                                             'line_2': resume_line_2,    # Salary, Lang, Schedule, Location...
                                                             'line_3': resume_line_3,    # Experience (position, description)
                                                             'resume_skills': resume_skills,
                                                             'line_1_en': transtator.translate(resume_line_1),
                                                             'line_2_en': transtator.translate(resume_line_2),
                                                             'line_3_en': transtator.translate(resume_line_3[:4999]),}})
        except Exception as ex:
            print('Ex.2. Resumes_collection.find_one_and_update:', ex)

    try:
        resume = await resumes_collection.find_one({'_id': resume_file_name})
        resume_skills = resume['resume_skills']
        r1 = resume['line_1_en']
        # print(r1) # Position, Skills, Add.Skills
        r2 = resume['line_2_en']
        # print(r2) # Salary, Languages, Job schedule, Location, Relocation, Total experience
        r3 = resume['line_3_en']
        # print(r3) # Experience (position + description)

        scores_ids = ids_and_scores(r1 + r2 + r3, db_index, k=k)
        return scores_ids, resume_skills, r1, r2, r3
    except Exception as ex:
        print('Ex.3. Resumes_collection.find_one:', ex)
        return
