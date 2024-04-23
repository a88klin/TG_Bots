from processing.start_mongodb import resumes_collection
from processing.vacansy_processing import db_index_vacancies
from processing.resume_processing import processing_resume_and_similarity_vacancies, get_vacancy
from processing.report_processing import create_pdf
from processing import prompts
from settings import settings
from openai import AsyncOpenAI
from aiogram.types import Message
import os


os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()
PDF_REPORT_FILES = settings.pdf_report_files
AMOUNT = 0


def print_tokens_count_and_price(completion):
    # 07/03/2024 - https://openai.com/pricing
    # gpt-3.5-turbo-0125 - Input: $0.50 / 1M tokens - Output: $1.50 / 1M tokens
    price = 0.5 * completion.usage.prompt_tokens / 1e6 + \
            1.5 * completion.usage.completion_tokens / 1e6
    print(f'Использовано токенов: {completion.usage.prompt_tokens} + '
                                f'{completion.usage.completion_tokens} = '
                                f'{completion.usage.total_tokens}. '
                                f'Цена: $ {round(price, 5)}')
    global AMOUNT
    AMOUNT += price


async def answer_gpt(messages, temp=0.3):
    completion = await AsyncOpenAI().chat.completions.create(
                       model="gpt-3.5-turbo-0125",
                       messages=messages,
                       temperature=temp)
    print_tokens_count_and_price(completion)
    return completion.choices[0].message.content


async def get_answer_gpt(message: Message, resume_file_name, k=5):
    from handlers.handlers import add_values
    global add_values
    try:
        scores_ids, resume_skills, r1, r2, r3 = \
            await processing_resume_and_similarity_vacancies(resume_file_name, db_index_vacancies, k=k)
    except Exception as ex:
        print('Ex.4. Similarity:', ex)
        return

    # Определение основного Скилла и опыта *********************************
    content_for_main_skill = [{"role": "system", "content": prompts.system},
                              {"role": "user", "content": f"{prompts.main_skill(r1, r3)}"}]
    response_main_skill = await answer_gpt(content_for_main_skill, temp=0)

    list_missing_skills = []
    list_conclusion = []
    # ***********************************************************************
    for vacancy_id in scores_ids[1][:1]: # по выбранным вакансиям _id
        vacancy_skills, chosen_vacancy = await get_vacancy(vacancy_id)

        # Выявление недостающих навыков от ChatGPT ***************************
        message_0 = [{"role": "system", "content": prompts.system},
                     {'role': 'assistant', 'content': prompts.assistant_0},
                     {"role": "user",
                     "content": f"{prompts.question_skills(resume_skills, vacancy_skills)}"}]
        response_missing_skills = await answer_gpt(message_0, temp=0.3)
        list_missing_skills.append({vacancy_id: response_missing_skills})

        try: # собираю недостающие скилы из ближайших вакансий
            add_values[message.from_user.id]['missing_skills'].update(eval(response_missing_skills))
        except Exception as ex:
            print('All_missing_skills:', ex)

        # Общее заключение от ChatGPT ****************************************
        message_1 = [{"role": "system", "content": prompts.system},
                     {"role": "user",
                      "content": f"{prompts.message_content_01(r1 + r2 + r3, chosen_vacancy)}"
                                 f"\n{prompts.question_skills_3(resume_skills, vacancy_skills)}"}]
        response_conclusion = await answer_gpt(message_1, temp=0.3)
        list_conclusion.append({vacancy_id: response_conclusion})

        try: # PDF отчет. Анализ резюме и вакангсии ****************************
            pdf_file_name = f"{resume_file_name[:-5]}_-_{vacancy_id[:-5]}.pdf"
            path = os.path.join(f'{PDF_REPORT_FILES}', pdf_file_name)
            paragraphs = [f"Резюме: {resume_file_name}",
                          f"Вакансия: {vacancy_id}",
                          f"{response_conclusion}",
                          f"{response_main_skill}",
                          # f"Не указанные в резюме навыки: {response_missing_skills}"
                          ]
            create_pdf(path, paragraphs)
            # session_pdf_files.append(path) # добавление названия pdf файла
            add_values[message.from_user.id]['pdf_files'].append(path)
        except Exception as ex:
            print('PDF отчет:', ex)

    try: # Запись ответов ChatGPT в коллекцию БД *******************************
        await resumes_collection.find_one_and_update(
                    {'_id': resume_file_name},
                    {'$set': {'missing_skills': list_missing_skills,
                              'conclusion': list_conclusion,
                              'main_skill': response_main_skill}})
    except Exception as ex:
        print('Missing_skills and conclusion update:', ex)

    add_values[message.from_user.id]['resume_id'] = resume_file_name
    print(round(AMOUNT, 5))
    return f'Резюме обработано! Наиболее подходящие вакансии: ' \
           f'\n\n{(", ").join(scores_ids[1])}'
