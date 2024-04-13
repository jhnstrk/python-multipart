ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}

# RUN useradd --create-home --home-dir /app \
#   --shell /bin/bash --uid 1001 appuser

# USER appuser

RUN python -m venv /app/.venv
# Enable venv
ENV PATH="/app/.venv/bin:$PATH"

RUN python -m pip install --upgrade pip

WORKDIR /app

COPY ./requirements.txt .

# COPY --chown=appuser . .
COPY . .

RUN --mount=type=cache,target=/root/.cache/pip \
  pip install .[dev]
