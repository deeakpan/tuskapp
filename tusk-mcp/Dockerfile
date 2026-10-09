# MSFLib lives in a private GitHub repo. Railway passes the service variable
# GITHUB_TOKEN in as a build arg; it is only used in the build stage, so it never
# ends up in the final image.
FROM python:3.12-slim AS build

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_SYSTEM_GIT_CLIENT=true \
    PIP_NO_CACHE_DIR=1
RUN pip install "poetry==2.5.1"

WORKDIR /app
COPY pyproject.toml poetry.lock poetry.toml ./

ARG GITHUB_TOKEN
RUN test -n "$GITHUB_TOKEN" || { echo "GITHUB_TOKEN is not set: add it to the Railway service variables" >&2; exit 1; } \
    && git config --global url."https://x-access-token:${GITHUB_TOKEN}@github.com/msflib/".insteadOf "https://github.com/msflib/" \
    && poetry install --only main --no-root \
    && rm -f /root/.gitconfig

FROM python:3.12-slim

WORKDIR /app
# /data is where the Railway volume mounts; without one, data resets on every deploy.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    SQLITE_DATABASE_URI=sqlite:////data/tusk.db \
    STORAGE_PATH=/data/uploads
RUN mkdir -p /data/uploads

COPY --from=build /app/.venv /app/.venv
COPY tusk_mcp ./tusk_mcp

CMD ["python", "-m", "tusk_mcp.app"]
