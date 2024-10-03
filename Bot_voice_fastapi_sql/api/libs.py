from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from set.config import config # путь от main.py
import os
from google.cloud import speech  # pip install google-cloud-speech


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'C:\_PY_Projects\LLM\v002_bot_v001+sql\set\service.json'
os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY.get_secret_value()
# os.environ["TAVILY_API_KEY"] = config.TAVILY_API_KEY.get_secret_value()
os.environ["LANGCHAIN_API_KEY"] = config.LANGCHAIN_API_KEY.get_secret_value()
os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGCHAIN_TRACING_V2"] = "true"


client_google_STT = speech.SpeechClient()
user_buffer_memory = dict()


# Очистка контекстной памяти диалога
async def clear_memory(tg_id: str):
    try: del user_buffer_memory[tg_id]
    except: pass


# Функция подсчета количества используемых токенов и стоимости
# https://openai.com/pricing
async def tokens_count_and_price(completion, model):
    if model == "gpt-4o-mini":
        input_price, output_price = 0.15, 0.60  # Устанавливаем цены
        price = input_price * completion.usage.prompt_tokens / 1e6 + \
                output_price * completion.usage.completion_tokens / 1e6  # Рассчитываем стоимость
        values = {'price': price,
                  'input': completion.usage.prompt_tokens,
                  'output': completion.usage.completion_tokens,
                  'total': completion.usage.total_tokens}  # Сохраняем значения
        print(f"Tokens used: {values['input']} + {values['output']} = {values['total']}. "
              f"*** {model} *** $ {round(values['price'], 8)}\n")  # Выводим информацию о токенах
        return values


async def answer_gpt(history: str, user_question: str, model="gpt-4o-mini", temp=0.3):
    messages = [
        {"role": "system", 
         "content": 'Ответь на вопрос пользователя с учетом контекста предыдущей переписки в формате MarkDown'},
        {"role": "user", 
         "content": f'Вот истоия переписки: {history} \n\nВот вопрос пользователя: {user_question}'}]
    completion = await AsyncOpenAI().chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp)
    await tokens_count_and_price(completion, model)
    return completion.choices[0].message.content


async def answer_gpt_memory(user_question: str, tg_id: str):
    if tg_id not in user_buffer_memory:
        user_buffer_memory[tg_id] = ConversationSummaryBufferMemory(
                                        llm=ChatOpenAI(model='gpt-4o-mini'),                                     
                                        max_token_limit=2000)
          
    # print(user_buffer_memory[tg_id])

    history = await user_buffer_memory[tg_id].aload_memory_variables({})
    if isinstance(history['history'], str): # если строка
        sum_history = history['history']
    else:  # если спискок
        sum_history = "\n".join(message.content for message in history['history']) 
        
    answer = await answer_gpt(sum_history, user_question)
    await user_buffer_memory[tg_id].asave_context({"input": user_question}, {"output": answer})
    return answer


async def stt(voice, client=client_google_STT):
    audio = speech.RecognitionAudio(content=voice)
    config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,
            language_code="ru-RU")
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript
    