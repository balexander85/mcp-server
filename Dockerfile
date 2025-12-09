FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml config.json src/ ./

# Run the MCP server with SSE transport
CMD ["uv", "tool", "run", "mcpo", "--port", "8000", "--config", "config.json", "--hot-reload"]
