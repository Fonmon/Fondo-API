#!/bin/bash
set -x

######################################################
# Script that trigger deploy process for api layer   #
# in server side.                                    #
######################################################

if [ $CODEBUILD_WEBHOOK_EVENT -eq 'PUSH' ] && [ $CODEBUILD_WEBHOOK_HEAD_REF -eq 'refs/heads/master' ]; then
	# Triggering deploy process
	echo 'Starting trigger'
	aws ssm send-command \
		--document-name "AWS-RunShellScript" \
		--comment "Deploying api layer" \
		--instance-ids "i-06e827f552c3f56a0" \
		--parameters commands="entrypoint_deploy master api master" \
		--output text
	echo 'Deploying in background'
	exit 0
fi