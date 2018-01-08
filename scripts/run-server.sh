#!/bin/bash

#################################################
# Use only in container or remove cd statement. #
#################################################

cd /app

pip install -r requirements.txt

python manage.py makemigrations fondo_api && python manage.py migrate

gunicorn --bind 0.0.0.0:8443 api.wsgi\
	--log-level=debug\
	-w 3
	--keyfile=certificates/privkey.pem\
	--ca-certs=certificates/chain.pem\
	--certfile=certificates/cert.pem