import logging, requests, json
from channels.consumer import SyncConsumer

logger = logging.getLogger(__name__)

class NotificationTaskConsumer(SyncConsumer):
    def send_notification(self, message):
        logger.info("Sending request to MNS...")
        request = requests.post('http://localhost:9901/mns/send', \
            data = json.dumps(message['content']), \
            headers = { 'content-type': 'application/json' } \
        )

        # remove invalid subscriptions
        print(request.json())