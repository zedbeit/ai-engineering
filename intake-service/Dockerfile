FROM python:3.12-slim

# uv, pinned to the version used locally.
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Install dependencies first, in their own layer, so changing the code
# doesn't reinstall them.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Then the project itself.
COPY README.md ./
COPY src ./src
RUN uv sync --locked --no-dev

# Run as an ordinary user, with the database in /data so it can be a volume.
RUN useradd --create-home app && mkdir /data && chown app /data
USER app
ENV PATH="/app/.venv/bin:$PATH" INTAKE_DB_PATH=/data/intake.db
VOLUME /data

EXPOSE 8000
CMD ["uvicorn", "intake_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
