# build image
FROM python:3.11-slim-bookworm as builder

ENV DEBIAN_FRONTEND=noninteractive \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_HOME="/opt/poetry" \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1 \
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv" \
  BUILD_PACKAGES='build-essential curl' \
  PATH=$PATH:/opt/poetry/bin

WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./

RUN apt update \
  && apt install -y ${BUILD_PACKAGES} \
  && curl -sSL https://install.python-poetry.org | python - \
  && poetry install --only main \
  && apt remove -y ${BUILD_PACKAGES} ${AUTO_ADDED_PACKAGES} \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* /root/.cache /root/.local \
  && curl -sSL https://install.python-poetry.org | python3 - --uninstall \
  && rm -rf /opt/poetry

# operational image
FROM debian:bookworm-slim

COPY --from=builder $VENV_PATH $VENV_PATH
ENV PATH="/opt/pysetup/.venv/bin:$PATH"
COPY twilio-todoist-proxy.py /app/
COPY twilio-todoist-proxy.toml /etc/
RUN chmod +x /app/twilio-todoist-proxy.py
CMD ["/app/twilio-todoist-proxy.py"]
