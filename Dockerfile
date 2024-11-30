ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION}

# RUN useradd --create-home --home-dir /app \
#   --shell /bin/bash --uid 1001 appuser

# USER appuser
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.4.12 /uv /uvx /bin/

# Enable venv
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# COPY --chown=appuser . .
COPY . .

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --python ${PYTHON_VERSION} --frozen
