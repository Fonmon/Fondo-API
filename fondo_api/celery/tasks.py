import logging
import requests
import json
import os
from celery.decorators import task

from fondo_api.models import NotificationSubscriptions

logger = logging.getLogger(__name__)

@task(name = "send_notification")
def send_notification(message):
    logger.info("Sending request to MNS...")
    mns_host = os.environ.get('MNS_HOST', 'localhost')
    try:
        request = requests.post('http://{}:9901/mns/send'.format(mns_host), \
            data = json.dumps(message['content']), \
            headers = { 'content-type': 'application/json' }, \
            timeout = 120 \
        )
        # remove invalid subscriptions
        if request.status_code == requests.codes.ok:
            invalid_subscriptions = request.json()['invalid']
            __remove_invalid_subscriptions(invalid_subscriptions)
    except Exception as ex:
        logger.error("Error trying to connect to MNS service: {}".format(ex))

def __remove_invalid_subscriptions(subscriptions):
    for subscription in subscriptions:
        NotificationSubscriptions.objects.filter(subscription__endpoint=subscription['endpoint'] ).delete()