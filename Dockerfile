FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG USER=app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN addgroup --gid 65535 ${USER} && \
    adduser --shell /sbin/nologin --disabled-password \
    --no-create-home --uid 65535 --ingroup ${USER} ${USER} && \
    apt-get update && apt-get install -y jq && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY src/ src/

USER ${USER}:${USER}

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["/bin/bash", "-c", "sleep infinity"]
#ENTRYPOINT ["python3", "src/main.py"]