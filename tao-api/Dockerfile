ARG PYTHON_VERSION=3.13.2
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN mkdir data
RUN mkdir data/logs

RUN apt-get update -y
RUN apt-get install -y python3-dev build-essential pkg-config default-libmysqlclient-dev

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["fastapi", "run", "src/main.py"]