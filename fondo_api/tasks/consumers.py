import logging
import requests
import json
import os
from channels.consumer import SyncConsumer

from fondo_api.logic.notifications_logic import remove_invalid_subscriptions

logger = logging.getLogger(__name__)

class NotificationTaskConsumer(SyncConsumer):
    def send_notification(self, message):
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
                remove_invalid_subscriptions(invalid_subscriptions)

        except Exception as ex:
            logger.info("Error trying to connect to MNS service: {}".format(ex))