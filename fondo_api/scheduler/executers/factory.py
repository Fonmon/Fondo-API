from fondo_api.services.notification import NotificationService
from fondo_api.scheduler.executers.notification_executer import NotificationExecuter

def get_executer(type):
    if type == 0:
        return NotificationExecuter(NotificationService())
    raise Exception("Executer type {} does not exist.".format(type))