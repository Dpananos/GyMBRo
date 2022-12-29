# syntax=docker/dockerfile:1
FROM python:3.10-slim-buster
WORKDIR /code
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-c", "print('Hello World')"]
