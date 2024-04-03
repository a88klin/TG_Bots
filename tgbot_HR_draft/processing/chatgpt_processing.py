from processing.start_mongodb import resumes_collection
from processing.vacansy_processing import db_index_vacancies
from processing.resume_processing import processing_resume_and_similarity_vacancies, get_vacancy
from processing.report_processing import create_pdf
from processing import prompts
from settings import settings
from openai import AsyncOpenAI
import os


os.environ["OPENAI_API_KEY"] = settings.openai_api_key.get_secret_value()
PDF_REPORT_FILES = settings.pdf_report_files
all_missing_skills = set()
resume_id = None
AMOUNT = 0


def print_tokens_count_and_price(completion):
    # "gpt-3.5-turbo-0125" - Input: $0.50 / 1M tokens - Output: $1.50 / 1M tokens - 07/03/2024 - https://openai.com/pricing
    price = 0.5 * completion.usage.prompt_tokens / 1e6 + 1.5 * completion.usage.completion_tokens / 1e6
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


async def get_answer_gpt(resume_file_name, k=3):
    try:
        scores_ids, resume_skills, r1, r2, r3 = \
            await processing_resume_and_similarity_vacancies(resume_file_name, db_index_vacancies, k=k)
    except Exception as ex:
        print('Ex.4. Similarity:', ex)
        return

    global all_missing_skills
    all_missing_skills.clear()

    list_missing_skills = []
    list_conclusion = []

    for vacancy_id in scores_ids[1][:1]: # по выбранным резюме _id
        vacancy_skills, chosen_vacancy = await get_vacancy(vacancy_id)

        # Выявление недостающих навыков от ChatGPT ***************************
        message_0 = [{"role": "system", "content": prompts.system_0},
                     {'role': 'assistant', 'content': prompts.assistant_0},
                     {"role": "user",
                     "content": f"{prompts.question_skills(resume_skills, vacancy_skills)}"}]
        response_missing_skills = await answer_gpt(message_0, temp=0.3)
        list_missing_skills.append({vacancy_id: response_missing_skills})

        try: # собираю недостающие скилы из ближайших вакансий
            all_missing_skills.update(eval(response_missing_skills))
        except Exception as ex:
            print('All_missing_skills:', ex)

        # Общее заключение от ChatGPT ****************************************
        message_1 = [{"role": "system", "content": prompts.system_0},
                     {'role': 'assistant', 'content': prompts.assistant_1},
                     {"role": "user",
                      "content": f"{prompts.message_content_01(r1 + r2 + r3, chosen_vacancy)}"
                                 f"\n{prompts.question_01(resume_skills, vacancy_skills)}"
                                 f"\n{prompts.question_02()}"
                                 f"\n{prompts.question_03()}"}]
        response_conclusion = await answer_gpt(message_1, temp=0.3)
        list_conclusion.append({vacancy_id: response_conclusion})

        try: # PDF отчет ******************************************************
            paragraphs = [f"Резюме: {resume_file_name}",
                          f"Вакансия: {vacancy_id}",
                          f"Заключение: {response_conclusion}",
                          f"Не указанные в резюме навыки: {response_missing_skills}"]
            pdf_file_name = f"{resume_file_name[:-5]}_-_{vacancy_id[:-5]}.pdf"
            path = os.path.join(f'{PDF_REPORT_FILES}', pdf_file_name)
            create_pdf(path, paragraphs)
        except Exception as ex:
            print('PDF отчет:', ex)

    try: # Запись ответов ChatGPT в коллекцию БД *******************************
        await resumes_collection.find_one_and_update(
                    {'_id': resume_file_name},
                    {'$set': {'missing_skills': list_missing_skills,
                              'conclusion': list_conclusion}})
    except Exception as ex:
        print('Missing_skills and conclusion update:', ex)

    global resume_id
    resume_id = resume_file_name
    print(round(AMOUNT, 5))
    return 'Резюме обработано. Ответьте на уточняющие вопросы'
