from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from deep_translator import GoogleTranslator
from settings import settings
from tqdm import tqdm
import pymongo
import time
import json
import re
import os


VACANCIES_JSON_FILES = settings.vacancies_json_files
DB_INDEX_FILES = settings.db_index_files
MONGODB_HOST = settings.mongodb_host
os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()
transtator = GoogleTranslator(source='ru', target='en')
os.makedirs(settings.vacancies_json_files, exist_ok=True)
os.makedirs(settings.db_index_files, exist_ok=True)


def update_vacancies():
    mongo = pymongo.MongoClient(MONGODB_HOST)
    vacancies_collection = mongo.hr.vacancies_bot

    new_chunks_vanacies = []
    for vacancy_file_name in tqdm(os.listdir(VACANCIES_JSON_FILES)):  # Локальная папка с вакансиями
        if vacancy_file_name.endswith('.json'):
            if not vacancies_collection.find_one({'_id': vacancy_file_name}):  # если вакансии нет в базе
                with open(os.path.join(f'{VACANCIES_JSON_FILES}', vacancy_file_name), 'r', encoding='utf-8') as r:
                    vacancy = json.load(r)
                    vacancy['_id'] = vacancy_file_name  # Добавляю поле "_id" с именем файла

                # **************************************************************************************************
                vacancy_skills = (', ').join(vacancy['skills'])
                position_skills = re.sub(r'\s+', ' ', f"""
                                  Position: {vacancy['data'].get('position', '')}. 
                                  Skills: {(', ').join(vacancy['skills'])}. """)
                position_skills_en = transtator.translate(position_skills)
                time.sleep(1) # пауза для более корректной работы между запросами к бесплатному переводчику

                requirements1 = re.sub(r'\s+', ' ', f"""
                                Requirements: {(' ').join(vacancy['data'].get('mandatoryRequirements', ''))} """)
                requirements1_en = transtator.translate(requirements1)
                time.sleep(1)

                try:
                    requirements2 = re.sub(r'\s+', ' ', f"""
                                    Add.Requirements: {(' ').join(vacancy['data']['additionalRequirements'])} """)
                    requirements2_en = transtator.translate(requirements2)
                    time.sleep(1)
                except Exception as ex:
                    # print(vacancy_file_name, 'Add.Requirements:', ex)
                    requirements2, requirements2_en = '', ''

                try:
                    # salary = int(re.findall(r'\d+', f"{vacancy['data']['partnerRates']}")[0]) * 168  # 168 часов в месяц
                    # salary = f"Salary: {salary} рублей в месяц. "
                    salary = int(re.findall(r'\d+', f"{vacancy['data']['partnerRates']}")[0])
                    salary = f"Ставка: {salary} рублей. "
                    salary_en = f"Salary Rate: {salary} rubles. "
                except Exception as ex:
                    salary, salary_en = '', ''

                levels = f"Levels: {(', ').join(vacancy['data'].get('experienceLevels', ''))}. "
                levels_en = transtator.translate(levels)

                format = f"Work Format: {vacancy['data'].get('workFormat', '')}. "
                format_en = transtator.translate(format)

                location = f"Required Location: {vacancy['data'].get('requiredLocation', '')}. "
                location_en = transtator.translate(location)
                time.sleep(1)

                try:
                    tasks = re.sub(r'\s+', ' ', f"Tasks: {(' ').join(vacancy['data']['projectTasks'])} ")
                    tasks_en = transtator.translate(tasks)
                    time.sleep(1)
                except Exception as ex:
                    # print(vacancy_file_name, 'Tasks:', ex)
                    tasks, tasks_en = '', ''

                # ********************************************************************************************
                try:  # сохраняю JSON и сформированные строки из полей вакансий в коллекцию vacancies
                    vacancies_collection.insert_one(vacancy)
                    vacancies_collection.find_one_and_update({'_id': vacancy['_id']},  # нахожу вакансию по _id
                                                             {'$set': {'vacancy_skills': vacancy_skills,
                                                                       'position_skills': position_skills,
                                                                       'position_skills_en': position_skills_en,
                                                                       'requirements1': requirements1,
                                                                       'requirements1_en': requirements1_en,
                                                                       'requirements2': requirements2,
                                                                       'requirements2_en': requirements2_en,
                                                                       'salary': salary,
                                                                       'salary_en': salary_en,
                                                                       'levels': levels,
                                                                       'levels_en': levels_en,
                                                                       'format': format,
                                                                       'format_en': format_en,
                                                                       'location': location,
                                                                       'location_en': location_en,
                                                                       'tasks': tasks,
                                                                       'tasks_en': tasks_en,
                                                                       }})
                except Exception as ex:
                    print('Save to vacancies_collection:', ex)

                vacancy_string_en = re.sub(r'\s+', ' ', position_skills_en +
                                                        requirements1_en +
                                                        requirements2_en +
                                                        levels_en +
                                                        salary_en +
                                                        format_en +
                                                        location_en +
                                                        tasks_en)

                new_chunks_vanacies.append(Document(page_content=vacancy_string_en,
                                                    metadata={'file': vacancy_file_name}))

    # *************************************************************************************
    if len(new_chunks_vanacies):

        db_index_new = FAISS.from_documents(new_chunks_vanacies, OpenAIEmbeddings())

        if os.path.exists(os.path.join(f'{DB_INDEX_FILES}', 'db_vacancies_index.faiss')):
            db_index_vacancies = FAISS.load_local(folder_path=DB_INDEX_FILES,
                                                  embeddings=OpenAIEmbeddings(),
                                                  index_name='db_vacancies_index')
            db_index_vacancies.merge_from(db_index_new)
            db_index_vacancies.save_local(folder_path=DB_INDEX_FILES,
                                          index_name='db_vacancies_index')
            print(len(db_index_vacancies.docstore._dict))

        else:
            db_index_new.save_local(folder_path=DB_INDEX_FILES,
                                    index_name='db_vacancies_index')
            print(len(db_index_new.docstore._dict))


if __name__ == "__main__":
    update_vacancies()
