FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /code

RUN apt-get update && apt-get install -y make

COPY pyproject.toml uv.lock README.md /code/
COPY src/smetapp/__init__.py /code/src/smetapp/
RUN uv sync --locked

COPY . /code/
