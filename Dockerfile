FROM python:3.12-slim

WORKDIR /mafia

COPY poetry.lock pyproject.toml .env alembic.ini ./

RUN python -m pip install --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.create false \
    && poetry install --without lint --no-interaction --no-ansi \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY bot ./bot