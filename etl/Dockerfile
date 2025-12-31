FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DAGSTER_HOME=/opt/dagster/dagster_home

WORKDIR /app

RUN apk add --update --no-cache \
    build-base \
    libpq-dev \
    && pip install poetry

COPY ./pyproject.toml ./poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

RUN mkdir -p /opt/dagster/dagster_home

COPY ./src /app/src
COPY ./alembic.ini /app/

EXPOSE 3000

ENTRYPOINT poetry run dagster dev -h 0.0.0.0 -p 3000
