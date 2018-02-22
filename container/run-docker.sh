#!/bin/bash
set -x

cd $HOME_FONMON

docker run -d --expose 8443 \
	--link fondo_db \
	--env-file=deploy/.env \
	--name fondo_api \
	--net fondo_network\
	fonapi_image:$1
