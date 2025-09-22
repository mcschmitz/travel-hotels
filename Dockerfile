# Install uv
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

COPY pyproject.toml /app/
COPY uv.lock /app/

# Install dependencies into a virtual environment
RUN uv sync --locked --no-install-project --no-editable

# Copy the project source code
COPY src /app/src

# Sync the project
RUN uv sync --locked --no-editable

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the virtual environment, source code, and pyproject.toml from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Make sure the virtual environment is in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run the application using the virtual environment's python
CMD ["python", "-m", "uvicorn", "src.main:create_app", "--host", "0.0.0.0", "--port", "8000"]
