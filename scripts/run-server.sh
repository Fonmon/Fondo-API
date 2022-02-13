#!/bin/bash

#################################################
# Use only in container or remove cd statement. #
#################################################

cd /app

if [ $# -ne 1 ]; then
	echo 'One argument must to be provided. {api|worker|scheduler|sch_work}'
	exit 1
fi

if [ $1 == 'api' ]; then
	python manage.py migrate

	gunicorn --bind 0.0.0.0:8443 api.wsgi\
		--log-level=debug\
		-w 3
fi
if [ $1 == 'worker' ]; then
	celery -A api worker -l info
fi
if [ $1 == 'scheduler' ]; then
	celery -A api beat -l info
fi
if [ $1 == 'sch_work' ]; then
	celery -A api worker -B -l info
fi