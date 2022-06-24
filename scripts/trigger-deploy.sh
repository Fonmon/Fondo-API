#!/bin/bash
set -x

######################################################
# Script that trigger deploy process for api layer   #
# in server side.                                    #
######################################################

# Arguments length: 2
# 1: commit number
# 2: instance ID
# 3: env
if [  $# -ne 3 ]; then
	echo 'Arguments: commit_revision instance_id {master|develop}'
	exit 1
fi

COMMIT=$1
INSTANCE=$2
ENV=$3

# Triggering deploy process
echo 'Starting trigger'
# aws ssm send-command \
# 	--document-name "AWS-RunShellScript" \
# 	--comment "Deploying api layer" \
# 	--instance-ids "${INSTANCE}" \
# 	--parameters commands="entrypoint_deploy ${COMMIT} api ${ENV}" \
# 	--output text
gcloud auth login $CLOUDSDK_ACCOUNT --cred-file=${HOME}/gcloud-service-key.json
gcloud compute ssh \
	--zone 'us-central1-a' \
	"${INSTANCE}" \
	--command "entrypoint_deploy ${COMMIT} api ${ENV}"
echo 'Deploying in background'
exit 0
