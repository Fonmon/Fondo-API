#!/bin/bash

#################################################
# Use only in container or remove cd statement. #
#################################################

cd /app

if [ $# -ne 1 ]; then
	echo 'One argument must to be provided. {api|worker}'
	exit 1
fi

if [ $1 == 'api' ]; then
	python manage.py migrate

	gunicorn --bind 0.0.0.0:8443 api.wsgi\
		--log-level=debug\
		-w 3
else
	daphne -p 9902 fondo_api.asgi:application
fi