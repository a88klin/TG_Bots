# базовый образ
FROM python:3.11

# рабочая директория
WORKDIR /Projects/v003

COPY requirements.txt ./

# установка библиотек
RUN pip install --no-cache-dir -r requirements.txt

# копируем проект
COPY . .

# запуск бота
CMD ["python", "bot.py"]
