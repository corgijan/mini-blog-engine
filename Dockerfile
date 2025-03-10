FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync


# Run app.py when the container launches
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0"]
