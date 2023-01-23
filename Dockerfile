# syntax=docker/dockerfile:1

FROM python:3.9.16-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src/* .src/
COPY settings.json .

CMD [ "python3", "src/main.py", "--watermark", "--deletion-attack"]