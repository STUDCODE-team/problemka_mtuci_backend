FROM python:3.12-slim

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Устанавливаем рабочую директорию на уровень монорепо
WORKDIR /app

# Копируем только необходимые папки: сервис и общую библиотеку
COPY services/auth ./services/auth
COPY libs/common ./libs/common

# Переходим в сервис auth
WORKDIR /app/services/auth

# Устанавливаем зависимости сервиса + локальные пакеты (common)
RUN poetry install --no-root --without dev

# Добавляем путь к корню для импортов из libs
ENV PYTHONPATH="/app"

# Запуск приложения
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
