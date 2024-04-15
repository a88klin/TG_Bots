from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.text import Const, Format, Case, List, Multi
from aiogram_dialog.widgets.kbd import Button, Row, Start, Cancel, Next, Back, SwitchTo
from dbase.database import add_user_data


class Check(StatesGroup):
    initial = State()
    name_check = State()
    name_edit = State()
    dob_check = State()
    dob_edit = State()
    position_check = State()
    position_edit = State()
    skills_check = State()
    skills_edit = State()

# --------------------------------------------------------------------------
async def set_data(dialog_manager: DialogManager, initial_data):
    dialog_manager.dialog_data['full_name'] = initial_data.get('full_name', 'Not found')
    dialog_manager.dialog_data['dob'] = initial_data.get('dob', 'Not found')
    dialog_manager.dialog_data['position'] = initial_data.get('position', 'Not found')
    dialog_manager.dialog_data['skills'] = initial_data.get('skills', 'Not found')


async def get_full_name(dialog_manager: DialogManager, **kwargs):
    return {'full_name': dialog_manager.dialog_data.get('full_name', 'Not found')}

async def get_dob(dialog_manager: DialogManager, **kwargs):
    return {'dob': dialog_manager.dialog_data.get('dob', 'Not found')}

async def get_position(dialog_manager: DialogManager, **kwargs):
    return {'position': dialog_manager.dialog_data.get('position', 'Not found')}

async def get_skills(dialog_manager: DialogManager, **kwargs):
    return {'skills': dialog_manager.dialog_data.get('skills', 'Not found')}


async def save_data_user(dialog_manager: DialogManager):
    update_data = {'full_name': dialog_manager.dialog_data.get('full_name', 'Not found'),
                   'dob': dialog_manager.dialog_data.get('dob', 'Not found'),
                   'position': dialog_manager.dialog_data.get('position', 'Not found'),
                   'skills': dialog_manager.dialog_data.get('skills', 'Not found')}
    all_message = dialog_manager.dialog_data['all_message']
    user_id = dialog_manager.dialog_data['user_id']

    await add_user_data(user_id, update_data, all_message) # Сохранение в базу данных

# ----------------------------------------------------------------------------
async def edit_name_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str):
    # dialog_manager.show_mode = ShowMode.SEND
    dialog_manager.dialog_data['full_name'] = text
    print(await get_full_name(dialog_manager))
    await message.answer(text=f'Вы указали полное имя: {text}')
    await dialog_manager.next()


async def edit_dob_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str):
    # dialog_manager.show_mode = ShowMode.SEND
    dialog_manager.dialog_data['dob'] = text
    print(await get_dob(dialog_manager))
    await message.answer(text=f'Вы указали дату рождения: {text}')
    await dialog_manager.next()


async def edit_position_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str):
    # dialog_manager.show_mode = ShowMode.SEND
    dialog_manager.dialog_data['position'] = text
    print(await get_position(dialog_manager))
    await message.answer(text=f'Вы указали position: {text}')
    await dialog_manager.next()


async def edit_skills_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str):
    # dialog_manager.show_mode = ShowMode.NO_UPDATE
    dialog_manager.dialog_data['skills'] = text
    print(await get_skills(dialog_manager))
    await message.answer(text=f'Вы указали skills: {text}')
    await save_data_user(dialog_manager)
    await message.answer('До свидания!')
    await dialog_manager.done()

async def close_dialog(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager):
    await save_data_user(dialog_manager)
    await callback.message.edit_text('До свидания!')
    await dialog_manager.done()

# ------------------------------------------------------------
main_dialog = Dialog(

    Window( # 0
        Const('Давайте проверим предоставленную вами информацию'),
        Row(Button(Const('До свидания'), id='close_dialog', on_click=close_dialog),
            Next(Const('✅ Согласен')),),
        state=Check.initial),

    Window( # 1
        Format(text='Полное имя: {full_name} ?'),
        Row(Next(Const('Изменить')),
            SwitchTo(Const('✅ Верно!'), id='from_1_to_3', state=Check.dob_check),),
        getter=get_full_name,
        state=Check.name_check,),

    Window( # 2
        Const(text='Введите полное имя 👇'),
        TextInput(id='name_edit', on_success=edit_name_handler,),
        state=Check.name_edit,),

    Window( # 3
        Format(text='Дата рождения: {dob} ?'),
        Row(Next(Const('Изменить')),
            SwitchTo(Const('✅ Верно!'), id='from_3_to_5', state=Check.position_check),),
        getter=get_dob,
        state=Check.dob_check,),

    Window( # 4
        Const(text='Введите дату рождения 👇'),
        TextInput(id='dob_edit', on_success=edit_dob_handler,),
        state=Check.dob_edit,),

    Window( # 5
        Format(text='Position: {position} ?'),
        Row(Next(Const('Изменить')),
            SwitchTo(Const('✅ Верно!'), id='from_5_to_7', state=Check.skills_check),),
        getter=get_position,
        state=Check.position_check,),

    Window( # 6
        Const(text='Введите position 👇'),
        TextInput(id='position_edit', on_success=edit_position_handler,),
        state=Check.position_edit,),

    Window( # 7
        Format(text='Skills: {skills} ?'),
        Row(Next(Const('Изменить')),
            Button(text=Const('✅ Верно!'), id='close_dialog', on_click=close_dialog),),
        getter=get_skills,
        state=Check.skills_check,),

    Window( # 8
        Const(text='Введите skills 👇'),
        TextInput(id='skills_edit', on_success=edit_skills_handler,),
        state=Check.skills_edit,),
)
