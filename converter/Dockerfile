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
    # MoviePy dependencies
    ffmpeg \
    # cleanup
  && rm -rf /var/lib/apt/lists/* \
  && pip install --upgrade pip \
  && pip install poetry 

WORKDIR ${APP_HOME}

COPY poetry.lock pyproject.toml ${APP_HOME}
RUN poetry install --no-interaction --no-ansi

COPY . ${APP_HOME}

# Because this is a consumer, we don't need to expose any ports

CMD ["python3", "consumer.py"]
