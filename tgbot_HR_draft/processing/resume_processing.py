from processing.start_mongodb import resumes_collection, vacancies_collection
from processing.vacansy_processing import db_index_vacancies
from processing import prompts
from deep_translator import GoogleTranslator
from settings import settings
from openai import AsyncOpenAI
import json
import os
import re


RESUMES_JSON_FILES = settings.resumes_json_files
os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()
transtator = GoogleTranslator(source='ru', target='en')


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
            experience += f"Job experience {n+1}: Position - {place['position']}. \
                            Job description {n+1}: {place['description']} "

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
            resumes_collection.insert_one(resume)
            resumes_collection.find_one_and_update({'_id': resume['_id']}, # нахожу резюме по _id
                                                   {'$set': {'line_1': resume_line_1,    # Position, Skills, Add.skills
                                                             'line_2': resume_line_2,    # Salary, Lang, Schedule, Location...
                                                             'line_3': resume_line_3,    # Experience (position, description)
                                                             'line_1_en': transtator.translate(resume_line_1),
                                                             'line_2_en': transtator.translate(resume_line_2),
                                                             'line_3_en': transtator.translate(resume_line_3[:4999]),}})
        except Exception as ex:
            print('Ex.2:', ex)

    try:
        resume = await resumes_collection.find_one({'_id': resume_file_name})
        r1 = resume['line_1_en']
        # print(r1) # Position, Skills, Add.Skills
        r2 = resume['line_2_en']
        # print(r2) # Salary, Languages, Job schedule, Location, Relocation, Total experience
        r3 = resume['line_3_en']
        # print(r2) # Experience (position + description)
        return ids_and_scores(r1 + r2 + r3, db_index, k=k), r1, r2, r3
    except Exception as ex:
        print('Ex.3:', ex)
        return


def print_tokens_count_and_price(completion):
    # "gpt-3.5-turbo-0125" - Input: $0.50 / 1M tokens - Output: $1.50 / 1M tokens - 07/03/2024 - https://openai.com/pricing
    price = 0.5 * completion.usage.prompt_tokens / 1e6 + 1.5 * completion.usage.completion_tokens / 1e6
    print(f'Использовано токенов: {completion.usage.prompt_tokens} + '
                                f'{completion.usage.completion_tokens} = '
                                f'{completion.usage.total_tokens}. '
                                f'Цена запроса + ответ: $ {price}\n')


async def answer_gpt(messages, temp=0.3):
    completion = await AsyncOpenAI().chat.completions.create(
                       model="gpt-3.5-turbo-0125",
                       messages=messages,
                       temperature=temp)
    print_tokens_count_and_price(completion)
    return completion.choices[0].message.content


async def get_answer_gpt(resume_file_name, k=5):
    try:
        scores_ids, r1, r2, r3 = \
        await processing_resume_and_similarity_vacancies(resume_file_name, db_index_vacancies, k=k)
    except Exception as ex:
        print('Ex.4:', ex)
        return

    vacancy = await vacancies_collection.find_one({'_id': scores_ids[1][0]}) # 1я вакансия из списка
    #v_line_1_en. Position, Skills, M.Requirements, Add.Requirements
    #v_line_2_en. Levels, WorkFormat, Location, Salary
    #v_line_3_en. Project Tasks
    chosen_vacancy = vacancy['line_1_en'] + vacancy['line_2_en'] + vacancy['line_3_en']

    system = prompts.system_01()
    # assistant = prompts.assistant_01()
    message_content = prompts.message_content_01(r1 + r2 + r3, chosen_vacancy)
    question = prompts.question_01(r2, vacancy['line_2_en'])
    message = [{"role": "system", "content": system},
               # {'role': 'assistant', 'content': assistant},
               {"role": "user", "content": f"{message_content}\n{question}"}]
    # response = None
    response = await answer_gpt(message, temp=0.3)
    return f'\n\n{scores_ids[0]}, ' \
           f'\n\n{scores_ids[1]}, ' \
           f'\n-----------------------------------------------' \
           f'\n\n{resume_file_name}, ' \
           f'\n\nЗаключение к 1-й вакансии:' \
           f'\n\n{response}'
