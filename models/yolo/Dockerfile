FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:0.7.19 /uv /uvx /bin/

# https://github.com/ultralytics/ultralytics/issues/1270
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git-all \
    && rm -rf /var/lib/apt/lists/*

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["uv", "run", "main.py"]