FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app


RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync
COPY . .


# Run app.py when the container launches
CMD ["uv", "run", "flask", "run", "--host=0.0.0.0"]
