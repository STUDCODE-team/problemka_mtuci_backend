FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# --- metadata (для Docker cache) ---
COPY services/reports/pyproject.toml services/reports/poetry.lock ./services/reports/
COPY libs/common/pyproject.toml libs/common/poetry.lock ./libs/common/

# --- зависимости ---
ARG POETRY_GROUPS=main
WORKDIR /src/services/reports
RUN poetry install --no-root --only ${POETRY_GROUPS}

# --- код ---
WORKDIR /src
COPY services/reports ./services/reports
COPY libs/common ./libs/common

# для импорта общих библиотек
ENV PYTHONPATH=/src:/src/services/reports/src

EXPOSE 8000

WORKDIR /src/services/reports
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
