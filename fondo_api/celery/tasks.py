import logging
import requests
import json
import os
import boto3
from api.celery import app

from fondo_api.models import NotificationSubscriptions

logger = logging.getLogger(__name__)
sqs_client = boto3.client('sqs', region_name=os.environ['AWS_REGION'])

@app.task(name = "send_notification")
def send_notification(message):
    logger.info("Sending request to MNS...")
    queue_url = os.environ.get('NOTIFICATIONS_QUEUE_URL', None)
    try:
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message['content']),
        )
        logger.info("Message sent, id: {}".format(response["MessageId"]))
    except Exception as ex:
        logger.error("Error trying to connect to MNS service: {}".format(ex))

def __remove_invalid_subscriptions(subscriptions):
    for subscription in subscriptions:
        NotificationSubscriptions.objects.filter(subscription__endpoint=subscription['endpoint'] ).delete()