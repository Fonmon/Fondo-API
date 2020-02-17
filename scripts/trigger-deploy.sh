#!/bin/bash
set -x

PROJECT_ID=notificationstest-90976
gcloud config set project $PROJECT_ID

if [ $TRAVIS_BRANCH == 'master' ]; then
  TAG=stable
  SERVICE=fonmonapi
  SERVICE_WORKER=fonmonapi-worker
  SERVICE_SCHED=fonmonapi-sched
else
  TAG=dev
  SERVICE=fonmonapi-dev
  SERVICE_WORKER=fonmonapi-worker-dev
  SERVICE_SCHED=fonmonapi-sched-dev
fi

cd $TRAVIS_BUILD_DIR/container
docker build -t fonmon_api -f ./Dockerfile ..
docker tag fonmon_api:latest us.gcr.io/$PROJECT_ID/fonmon_api:$TAG

gcloud -q auth configure-docker
gcloud -q container images delete us.gcr.io/$PROJECT_ID/fonmon_api:$TAG --force-delete-tags
docker push us.gcr.io/$PROJECT_ID/fonmon_api:$TAG

gcloud -q run deploy $SERVICE --allow-unauthenticated --max-instances=1 --platform managed --region us-central1 --image us.gcr.io/$PROJECT_ID/fonmon_api:$TAG --update-env-vars=CURRENT_API_APP=api
gcloud -q run deploy $SERVICE_SCHED --no-allow-unauthenticated --max-instances=1 --platform managed --region us-central1 --image us.gcr.io/$PROJECT_ID/fonmon_api:$TAG --update-env-vars=CURRENT_API_APP=scheduler
gcloud -q run deploy $SERVICE_WORKER --no-allow-unauthenticated --max-instances=1 --platform managed --region us-central1 --image us.gcr.io/$PROJECT_ID/fonmon_api:$TAG --update-env-vars=CURRENT_API_APP=worker

exit 0