from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from keyboards.keyboards import digit_kb_inline
from processing.chatgpt_processing import all_missing_skills
from processing.start_mongodb import resumes_collection
from processing.report_processing import report_pdf


qs = [] # список недостающих навыков
router = Router()

class Question(StatesGroup):
    q0 = State()
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()


@router.callback_query(F.data=='_exit')
async def exit_message(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer('Обработка завершена. Вы можете загрузить следующее резюме в фомате JSON. '
                                  'После обработки резюме вам будет предложено ответить на вопросы')


@router.callback_query(F.data=='_yes') # начало опроса
async def question_0(callback: CallbackQuery, state: FSMContext):
    global qs
    qs = list(all_missing_skills) # подтягиваю недостающие навыки
    await state.set_state(Question.q0)
    await callback.message.delete()
    await callback.message.answer(f"Оцени от 0 до 7 владение навыком: '{qs[0]}'",
                                  reply_markup=digit_kb_inline())


@router.callback_query(Question.q0)
async def question_1(callback: CallbackQuery, state: FSMContext):
    await state.update_data(q0={qs[0]: callback.data}) # Ответ - оценка по навыку 0
    await state.set_state(Question.q1)
    await callback.message.delete()
    await callback.message.answer(f"Оцени от 0 до 7 владение навыком: '{qs[1]}'",
                                  reply_markup=digit_kb_inline())


@router.callback_query(Question.q1)
async def question_2(callback: CallbackQuery, state: FSMContext):
    await state.update_data(q1={qs[1]: callback.data}) # Ответ - оценка по навыку 1
    await state.set_state(Question.q2)
    await callback.message.delete()
    await callback.message.answer(f"Оцени от 0 до 7 владение навыком: '{qs[2]}'",
                                  reply_markup=digit_kb_inline())

@router.callback_query(Question.q2)
async def question_3(callback: CallbackQuery, state: FSMContext):
    await state.update_data(q2={qs[2]: callback.data}) # Ответ - оценка по навыку 2
    await state.set_state(Question.q3)
    await callback.message.delete()
    await callback.message.answer(f"Оцени от 0 до 7 владение навыком: '{qs[3]}'",
                                  reply_markup=digit_kb_inline())


@router.callback_query(Question.q3)
async def question_4(callback: CallbackQuery, state: FSMContext):
    await state.update_data(q3={qs[3]: callback.data}) # Ответ - оценка по навыку 3
    await state.set_state(Question.q4)
    await callback.message.delete()
    await callback.message.answer(f"Оцени от 0 до 7 владение навыком: '{qs[4]}'",
                                  reply_markup=digit_kb_inline())


@router.callback_query(Question.q4)
async def final_handler_questions(callback: CallbackQuery, state: FSMContext):
    await state.update_data(q4={qs[4]: callback.data}) # Ответ - оценка по навыку 4
    data = await state.get_data() # сохраненные ответы
    await state.clear()
    await callback.message.delete()

    missing_skill_value = ''
    missing_skill_value_dict = {}
    for inner_dict in data.values():
        k, v = next(iter(inner_dict.items()))
        missing_skill_value += f'{k}: {v}.  '  # Навык: оценка владения
        missing_skill_value_dict |= inner_dict  # объединенный словарь - Навык: оценка владения
    await callback.message.answer(f'Указанный уровень владения навыками от 0 до 7:  {missing_skill_value}')
    await callback.message.answer('Спасибо! Вам будут высланы подходящие вакансии.')

    # Запись ответов в коллекцию БД и создание отчета ***********************************
    try:
        from processing.chatgpt_processing import resume_id

        field_skill_value = bool(await resumes_collection.find_one( # есть ли уже запись в коллекции
                            {'_id': resume_id, 'missing_skill_value': {"$exists": True}}))

        if field_skill_value: # если запись в коллекции есть
            d_exists = await resumes_collection.find_one({'_id': resume_id},
                                                         {'missing_skill_value': 1})
            # объединение (обновление) словарей
            missing_skill_value_dict = d_exists['missing_skill_value'] | missing_skill_value_dict

        await resumes_collection.find_one_and_update( # сохранение ответов в коллекцию
                {'_id': resume_id},
                {'$set': {'missing_skill_value': missing_skill_value_dict}})

        await report_pdf(resume_id, missing_skill_value_dict) # создание PDF отчета

    except Exception as ex:
        print('missing_skill_value and report:', ex)