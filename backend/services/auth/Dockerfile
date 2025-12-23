FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src

RUN pip install --no-cache-dir poetry

# --- metadata ---
COPY services/auth/pyproject.toml services/auth/poetry.lock ./services/auth/
COPY libs/common/pyproject.toml libs/common/poetry.lock ./libs/common/

# --- deps ---
WORKDIR /src/services/auth
RUN poetry install --no-root --only main

# --- code ---
WORKDIR /src
COPY services/auth ./services/auth
COPY libs/common ./libs/common

# 🔑 ВАЖНО
ENV PYTHONPATH=/src:/src/services/auth/src

EXPOSE 8000

WORKDIR /src/services/auth
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
