#!/bin/bash
set -x

source /etc/environment
cd $HOME_FONMON/deploy

docker run -d --expose 8443 \
	--link fondo_db \
	--env-file=.env \
	--name fondo_api \
	--net fondo_network\
	fonapi_image:$1
