# базовый образ
FROM python:3.11

# рабочая директория
WORKDIR /Projects/hr_bot

# копируем проект
COPY . /Projects/hr_bot

# установка библиотек
RUN pip install -r requirements.txt

# запуск бота
CMD ["python", "bot.py"]
