#!/bin/bash

######################################################
# Script that trigger deploy process in server side. #
######################################################

# Arguments length: 1
# 1: commit number
if [  $# -ne 1 ]
then
	echo 'Missing commit argument'
	exit 1
fi

COMMIT=$1

echo 'Starting trigger'
# Triggering deploy process
aws ssm send-command \
	--document-name "AWS-RunShellScript" \
	--comment "Deploying app" \
	--instance-ids "i-032bb4826c0e1b2c2" \
	--parameters commands="deploy-app ${COMMIT}" \
	--output text
echo 'Finishing trigger'
exit 0