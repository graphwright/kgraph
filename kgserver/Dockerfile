# Multi-stage build for KG server
FROM python:3.13-slim AS builder

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# kgbundle is not on PyPI; copy source so uv can install it as a local dep
COPY kgbundle ./kgbundle

# Copy dependency files from kgserver
COPY kgserver/pyproject.toml ./
COPY kgserver/uv.lock ./

# Install ALL dependencies using uv (not pip)
RUN apt update && \
    apt install -y git vim ripgrep
# Re-lock after path fix, then sync with relocatable venv
RUN uv venv --python /usr/local/bin/python3 --relocatable && \
    uv lock && uv sync && \
    uv pip install uvicorn fastapi zensical \
        mkdocs mkdocs-material pymdown-extensions

# Docs: Track 2 set under docs/ + kgserver index as site home
COPY kgserver/mkdocs.yml ./
COPY docs/ ./docs/
COPY kgserver/index.md ./docs/index.md

# Prebuild MkDocs site so runtime does not run zensical build (avoids hang on small droplets)
RUN uv run zensical build

# Final stage - use same base image to keep Python paths consistent
FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 unzip curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the venv from builder (symlinks will work since same Python path)
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/docs /app/docs
COPY --from=builder /app/site /app/site
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY kgbundle ./kgbundle
COPY kgserver/ .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app:/app/kgbundle"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["tail", "-f", "/dev/null"]
