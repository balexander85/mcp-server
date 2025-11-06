FROM python:3.14-slim

# Set working directory
WORKDIR /app
ENV PYTHONPATH=/app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# Copy project files
COPY pyproject.toml config.json src/ ./

# Run the MCP server with SSE transport
CMD ["uv", "tool", "run", "mcpo", "--port", "8000", "--config", "config.json", "--hot-reload"]

