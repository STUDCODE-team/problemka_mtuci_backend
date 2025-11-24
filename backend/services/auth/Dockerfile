FROM python:3.12-slim

WORKDIR /app

# Ставим Poetry
RUN pip install --no-cache-dir poetry

# Копируем только pyproject, чтобы Poetry установил зависимости
COPY services/auth/pyproject.toml services/auth/poetry.lock ./services/auth/
COPY libs/common/pyproject.toml libs/common/poetry.lock ./libs/common/

# Ставим зависимости
WORKDIR /app/services/auth
RUN poetry install --no-root --without dev

# Добавляем путь к корню монорепо
ENV PYTHONPATH="/app"

# По умолчанию запускаем uvicorn с авто-перезагрузкой
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
