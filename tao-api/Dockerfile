ARG PYTHON_VERSION=3.11.8
FROM python:${PYTHON_VERSION}-bookworm as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN mkdir data
RUN mkdir data/logs

RUN apt-get update -y
RUN apt-get install -y python3-dev build-essential pkg-config default-libmysqlclient-dev git curl sudo nano netcat-openbsd wget unzip tmux apt-utils cmake

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "src/main.py"]