FROM python:3.12-slim-bookworm

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy the lockfile and `pyproject.toml` into the image
COPY uv.lock pyproject.toml /app/

# Install dependencies
RUN uv sync --frozen --no-install-project

# install application
COPY . /app/
RUN uv sync --frozen

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
