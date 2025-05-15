FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /api/
COPY . /api/

RUN uv venv

RUN uv pip install -r requirements.txt

ENV PATH="/api/.venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
