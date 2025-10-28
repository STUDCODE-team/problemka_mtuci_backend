FROM python:3.12-slim

WORKDIR /app
RUN pip install poetry

# Копируем весь проект — чтобы были и libs/, и services/
COPY . .

# Переходим в папку сервиса auth
WORKDIR /app/services/auth

# Устанавливаем зависимости
RUN poetry install --no-root --without dev

# <-- Добавляем путь к libs
ENV PYTHONPATH="/app"

# Запуск приложения
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
