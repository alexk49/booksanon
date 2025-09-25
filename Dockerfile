FROM python:slim

RUN python -m venv /venv

ENV PATH="/venv/bin:$PATH"

RUN pip install .

COPY src /src
COPY static /src/static

WORKDIR /src

CMD ["uvicorn", "src.server.app:app", "--host", "${HOST}", "--port", "${PORT}", "--workers", "${WORKERS}", "--log-level", "info"]
