# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл с зависимостями (создай его командой pip freeze > requirements.txt заранее!)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем все файлы проекта внутрь контейнера
COPY . .

# Указываем, что база данных будет храниться в виде постоянного тома
VOLUME ["/app/MetaPsy_biology.db"]

# Запускаем бота
CMD ["python", "bot.py"]
