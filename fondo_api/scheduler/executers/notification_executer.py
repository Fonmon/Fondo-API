from fondo_api.models import Loan
from fondo_api.scheduler.executers.abstract_executer import AbstractExecuter

class NotificationExecuter(AbstractExecuter):

    def __init__(self, notification_service):
        super().__init__()
        self.__notification_service = notification_service

    def run(self, payload):
        loan = Loan.objects.get(id = payload["loan_id"])
        self.__notification_service.send_notification(
            [loan.user.id], 
            payload["message"], 
            "/loan/{}".format(loan.id), 
            False
        )