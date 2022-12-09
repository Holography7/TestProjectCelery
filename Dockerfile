FROM python:3.11-alpine
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade wheel
# RUN apk add --no-cache gcc musl-dev python3-dev

WORKDIR /TODO_service
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src ./src
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh
WORKDIR /TODO_service/src
ENTRYPOINT ../docker-entrypoint.sh
