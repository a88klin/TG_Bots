import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
from set.config import config
from langchain_core.tools import tool


servise_json = config.GOOGLE_SERVICE_TAB
link_notepad = config.LINK_NOTEPAD
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
client_gs = gspread.authorize(
    ServiceAccountCredentials.from_json_keyfile_name(servise_json, scope))


@tool
def get_row(n: int, link=link_notepad) -> str:
    """
    Функция получения записи из строки из БЛОКНОТА по номеру.
    Args: n (int) - номер нужной строки.
          Например, n=-1 - это последняя строка (запись), n=1 - это первая строка (запись).
    return: (str) - вывод записи из блокнота по номеру строки
    """
    spreadsheet = client_gs.open_by_url(link)
    worksheet = spreadsheet.get_worksheet(0)  # доступ к первому листу
    all_values = worksheet.get_all_values()
    try:
        return f'Запись от {all_values[n][0]}:\n{all_values[n][1]}'
    except:
        return 'В блокноте нет записей'


@tool
def save_note(note: str, link=link_notepad) -> None:
    """
    Функция записи текстовой заметки в БЛОКНОТ.
    Args: note (str) - текст для записи в блокнот.
    """
    spreadsheet = client_gs.open_by_url(link)
    worksheet = spreadsheet.get_worksheet(0)  # доступ к первому листу
    date_time = datetime.now(pytz.timezone(
        'Europe/Moscow')).strftime("%Y-%m-%d %H:%M")
    try:  # Запись строки в конец листа
        worksheet.append_row(
            [date_time, note], value_input_option='USER_ENTERED')
    except Exception as ex:
        return f'save_note(): {ex}'
