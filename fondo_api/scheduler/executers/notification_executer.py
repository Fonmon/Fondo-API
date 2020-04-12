import json
from fondo_api.scheduler.executers.abstract_executer import AbstractExecuter

class NotificationExecuter(AbstractExecuter):

    def __init__(self, notification_service):
        super().__init__()
        self.__notification_service = notification_service

    def run(self, payload):
        user_ids = json.loads(payload["user_ids"])
        self.__notification_service.send_notification(
            user_ids, 
            payload["message"], 
            payload["target"], 
            False
        )