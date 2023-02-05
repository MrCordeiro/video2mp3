FROM python:3.10-slim-bullseye

ARG APP_HOME=/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_NO_INTERACTION 1
ENV POETRY_VIRTUALENVS_CREATE false
ENV POETRY_CACHE_DIR "/var/cache/pypoetry"
ENV POETRY_HOME "/usr/local"

RUN apt-get update --yes --quiet && apt-get install --no-install-recommends --no-install-suggests --yes --quiet \
    # dependencies for building Python packages
    build-essential \
    # psycopg2 dependencies
    libpq-dev \
    # cleanup
  && rm -rf /var/lib/apt/lists/*

WORKDIR ${APP_HOME}
COPY . ${APP_HOME}
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry install --no-interaction --no-ansi

EXPOSE 5000

CMD ["python3", "auth/server.py"]
