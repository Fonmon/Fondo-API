#!/bin/bash

cd /home/ubuntu/Fondo-DevOps/

docker run -d -p :8443 \
	--link fondo_db \
	--env-file=.env \
	--name fondo_api \
	--net fondo_network\
	fonapi_image:$1
