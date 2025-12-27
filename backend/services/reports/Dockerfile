FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# --- зависимости (для Docker cache) ---
COPY services/reports/pyproject.toml services/reports/poetry.lock ./services/reports/
COPY libs/common ./libs/common

ARG POETRY_GROUPS=main
WORKDIR /app/services/reports
RUN poetry install --no-root --only ${POETRY_GROUPS}

# --- код ---
WORKDIR /app
COPY services/reports ./services/reports

WORKDIR /app/services/reports/src
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
