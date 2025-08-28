FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

ENV PYTHONPATH=/app

COPY ./pyproject.toml ./requirements.txt /app/

RUN pip install -r /app/requirements.txt

COPY ./jobmanager /app/jobmanager

CMD ["fastapi", "run", "--workers", "4", "jobmanager/main.py"]