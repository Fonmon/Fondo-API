#!/bin/bash

#################################################
# Use only in container or remove cd statement. #
#################################################

cd /app

python manage.py makemigrations fondo_api && python manage.py migrate

gunicorn --bind 0.0.0.0:8443 api.wsgi\
	--log-level=debug\
	-w 3