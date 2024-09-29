from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from set.config import config
from langchain_core.tools import tool


service_file_calendar = config.GOOGLE_SERVICE_CALENDAR
service_file_token = config.GOOGLE_CALENDAR_TOKEN
SCOPES = ['https://www.googleapis.com/auth/calendar']


def create_token(servise_json=service_file_calendar,
                 token_json=service_file_token):
    creds = None
    # Файл token.json создается автоматически при первом запуске.
    if os.path.exists(token_json):
        creds = Credentials.from_authorized_user_file(token_json, SCOPES)
    # Если нет действительных учетных данных, запросите авторизацию пользователя.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                servise_json, SCOPES)
            creds = flow.run_local_server(port=0)
        # Сохраните учетные данные для следующего запуска
        with open(token_json, 'w') as token:
            token.write(creds.to_json())
    return creds


@tool
def create_event(summary: str,
                 description: str,
                 start: str,
                 end: str,
                 min_reminder=10):
    """
    Функция записывает в календарь мероприятие или задачу, дату и время начала, дату и время окончания
    Args:
        summary (str) - название или краткое описание мероприятия или задачи
        description (str) - дополнительное описание мероприятия или задачи (может быть пустым)
        start (str) - дата и время начала мероприятия или задачи по стандарту ISO 8601, например: '2024-09-25T19:00:00'
        end (str) - дата и время окончания мероприятия или задачи по стандарту ISO 8601, например: '2024-09-25T20:00:00'
    return: (str) - подтверждение создание записи
    """
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start,
                  'timeZone': 'Europe/Moscow', },
        'end': {'dateTime': end,
                'timeZone': 'Europe/Moscow', },
        'reminders': {'useDefault': False,
                      'overrides': [{'method': 'popup',
                                     'minutes': min_reminder}, ], }, }
    creds = create_token()
    service = build('calendar', 'v3', credentials=creds)
    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Событие создано: {event.get('htmlLink')}"
    except Exception as ex:
        return f'Calendar create_event(): {ex}'


@tool
def get_events(start_date: str,  # 'YYYY-MM-DD'
               end_date: str):   # 'YYYY-MM-DD'
    """
    Функция получает и показывает все записи из календаря о мероприятиях в заданном интервале дат
    с start_date по end_date
    Args:
        start_date (str) - дата начала интервала для выборки записей в формате: 'YYYY-MM-DD'
        end_date (str) - дата конца интервала для выборки записей в формате: 'YYYY-MM-DD'
    return: (str) - записи из календаря
    """
    creds = create_token()
    service = build('calendar', 'v3', credentials=creds)
    # Определяем временные рамки для запроса событий
    time_min = f'{start_date}T00:00:00Z'
    time_max = f'{end_date}T23:59:59Z'
    # Получаем события из календаря
    try:
        events_result = service.events().list(calendarId='primary',
                                              timeMin=time_min,
                                              timeMax=time_max,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            return 'Нет событий на указанные даты.'
        events_str = ''
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = datetime.fromisoformat(start).strftime('%Y-%m-%d %H:%M')
            events_str += f"{start} - {event['summary']} - {event['htmlLink']}\n"
        return f'События на указанные даты: {events_str}'
    except Exception as ex:
        return f'Calendar get_events(): {ex}'


@tool
def delete_event(start: str):
    """
    Функция удаляет запись о мероприятии из календаря по дате и времени начала.
    Args:
        start (str) - дата и время начала мероприятия по стандарту ISO 8601, например: '2024-09-25T19:00:00'
    return: (str) - подтверждение удаления записи
    """
    creds = create_token()
    service = build('calendar', 'v3', credentials=creds)
    # Уточняем временной интервал для поиска события
    time_min = (datetime.fromisoformat(start) -
                timedelta(seconds=0)).isoformat() + '+03:00'
    time_max = (datetime.fromisoformat(start) +
                timedelta(seconds=3600)).isoformat() + '+03:00'
    # Получаем список событий, чтобы найти нужное для удаления
    events_result = service.events().list(calendarId='primary',
                                          timeMin=time_min,
                                          timeMax=time_max,
                                          maxResults=1, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        return "Событие не найдено."
    # Удаляем найденное событие
    event_id = events[0]['id']
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"Событие: {events[0]['summary']} {events[0]['start']['dateTime']} - успешно удалено."
    except Exception as ex:
        return f'Calendar delete_event(): {ex}'
