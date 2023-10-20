from fondo_api.enums import EmailTemplate

class AdminService:

  def __init__(self, mail_service = None, notification_service = None):
    self.__mail_service = mail_service
    self.__notification_service = notification_service

  def test_email(self, user):
    self.__mail_service.send_mail(EmailTemplate.TEST, [user.email], None)

  def test_notifications(self, user):
    self.__notification_service.send_notification(
      [user.id],
      "Test Notification", 
			"/"
    )