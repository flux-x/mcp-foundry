FROM python:3.13-slim
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --upgrade pip && pip install uv
COPY pyproject.toml README.md /app/
RUN uv sync --no-dev
COPY . /app
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "mcp_foundry.main:app", "--host", "0.0.0.0", "--port", "8000"]
