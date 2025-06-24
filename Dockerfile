FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /mafia

RUN pip install --upgrade pip wheel "poetry==1.8.3"

RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml alembic.ini ./

RUN poetry install --without lint

COPY .env ./

COPY bot ./bot