FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .

RUN uv venv

RUN uv pip install -r requirements.txt

EXPOSE 9000

ENTRYPOINT ["uv", "run", "mcp_server.py"]
