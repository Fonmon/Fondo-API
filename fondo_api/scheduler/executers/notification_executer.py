import fondo_api.logic.notifications_logic as notification
from fondo_api.scheduler.executers.abstract_executer import AbstractExecuter
from fondo_api.models import Loan

class NotificationExecuter(AbstractExecuter):
    def run(self, payload):
        loan = Loan.objects.get(id = payload["loan_id"])
        notification.send_notification([loan.user.id], payload["message"], "/loan/{}".format(loan.id), False)