from fastapi import FastAPI, UploadFile
from typing import Dict
from api.libs import answer_gpt_memory, stt, clear_memory
from dbase.database import add_user, add_dialog, create_db
from pprint import pprint as pp


app = FastAPI(title="My_App")
# -----------------------------------------------------


@app.post("/gpt")
async def post_answer_gpt(query: Dict):
    answer = await answer_gpt_memory(query["text"], query["tg_id"])
    print('tg_id:', query["tg_id"])
    print(f'Ваше сообщение: {query["text"]} \nОтвет ChatGPT: {answer}')
    return answer


@app.get("/clear")
async def get_clear(query: Dict):
    await clear_memory(query["tg_id"])


@app.post("/upload-audio")
async def upload_audio(file: UploadFile):
    try:
        tg_id = file.filename.split('.')[0]
        audio_content = await file.read()
        text_message = await stt(audio_content)  # в текст
        answer = await answer_gpt_memory(text_message, tg_id)
        print('tg_id:', tg_id)
        print(
            f'Ваше аудио сообщение: {text_message} \nОтвет ChatGPT: {answer}')
        # return f'Ваше аудио сообщение: {text_message} \n\n{answer}'
        return {'text_message': text_message,
                'answer': answer}
    except Exception as ex:
        print(f"upload_audio: {ex}")
        return f"upload_audio: {ex}"


@app.post("/save_db")
async def save_to_db(query: Dict, new_db=False):
    if new_db:
        await create_db()  # удаление и создание новых баз
    try:
        await add_user(query)
    except Exception as ex:
        print('add_user:', ex)
    try:
        await add_dialog(query)
    except Exception as ex:
        print('add_dialog:', ex)
