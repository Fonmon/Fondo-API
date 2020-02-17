FROM python:3.6.6-alpine

WORKDIR /app

RUN apk update && \
    apk add postgresql-libs && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev && \
    apk add nginx

# Nginx configuration
RUN mkdir -p /run/nginx
RUN mkdir -p /run/nginx/tmp
COPY container/nginx.conf /etc/nginx/nginx.conf
COPY fondo_api/static/ /usr/share/nginx/html/static_files

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

RUN apk --purge del .build-deps

COPY . /app

ENTRYPOINT ["/bin/sh", "scripts/run-server.sh"]