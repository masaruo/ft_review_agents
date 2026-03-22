FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    make \
    build-essential \
    clang \
    valgrind \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .
# We use `uv lock` in case uv.lock isn't generated yet, then sync
RUN uv lock && uv sync --no-dev

COPY . /app

ENTRYPOINT ["uv", "run", "python", "main.py"]
