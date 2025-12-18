FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m app
USER app
WORKDIR /home/app

RUN python -m venv venv

ENV PATH="/home/app/venv/bin:$PATH"

COPY --chown=app:app requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt \
    && rm -rf /home/app/.cache/pip

COPY --chown=app:app src/ ./src
COPY --chown=app:app static/ ./static
COPY --chown=app:app templates/ ./templates

WORKDIR /home/app/src

CMD ["sh", "-c", "huey_consumer.py server.tasks.huey --workers=1 & uvicorn server.app:app --host ${HOST} --port ${PORT} --workers ${WORKERS} --log-level info"]
