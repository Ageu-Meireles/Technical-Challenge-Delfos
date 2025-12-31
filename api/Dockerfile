FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apk add --update --no-cache \
    build-base \
    libpq-dev \
    && pip install poetry

COPY ./pyproject.toml ./poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY ./alembic.ini /app/

EXPOSE 8000

ENTRYPOINT alembic upgrade head \
    && uvicorn src.main:app --port 8000 --loop uvloop --host 0.0.0.0 
