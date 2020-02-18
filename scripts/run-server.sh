#!/bin/bash

#################################################
# Use only in container or remove cd statement. #
#################################################

cd /app

if [ $CURRENT_API_APP == 'api' ]; then
	python manage.py migrate

	gunicorn --bind 0.0.0.0:8081 api.wsgi\
		--log-level=debug &
fi
if [ $CURRENT_API_APP == 'worker' ]; then
	celery -A api worker -l info &
fi
if [ $CURRENT_API_APP == 'scheduler' ]; then
	celery -A api beat -l info &
fi

nginx -g 'daemon off;'