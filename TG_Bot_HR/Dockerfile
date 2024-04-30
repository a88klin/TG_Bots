# базовый образ
FROM python:3.11

# рабочая директория
WORKDIR /Projects/hr_bot

COPY requirements.txt ./

# установка библиотек
RUN pip install -r requirements.txt

# копируем проект
COPY . .

# запуск бота
CMD ["python", "bot.py"]
