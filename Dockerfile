FROM python:slim

RUN python -m venv /venv

ENV PATH="/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY src /src
COPY static /static
COPY templates /templates

WORKDIR /src

CMD sh -c "huey_consumer.py server.tasks.huey --workers=1 & uvicorn server.app:app --host ${HOST} --port ${PORT} --workers ${WORKERS} --log-level info"
