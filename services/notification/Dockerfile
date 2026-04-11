FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY services/notification/pyproject.toml services/notification/poetry.lock* ./services/notification/
COPY libs/common ./libs/common

ARG POETRY_GROUPS=main
WORKDIR /app/services/notification
RUN poetry install --no-root --only ${POETRY_GROUPS}

WORKDIR /app
COPY services/notification ./services/notification

WORKDIR /app/services/notification/src
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
