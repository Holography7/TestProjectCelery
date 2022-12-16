FROM python:3.11-alpine

RUN apk update && apk add --no-cache supervisor
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade wheel

WORKDIR /TODO_service
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src ./src
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh
COPY supervisord.conf .
WORKDIR /TODO_service/src
CMD ["supervisord", "-c", "../supervisord.conf"]
