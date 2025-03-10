FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync


# Run app.py when the container launches
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0"]
