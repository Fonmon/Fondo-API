from fondo_api.enums import EmailTemplate

class AdminService:

  def __init__(self, mail_service = None):
    self.__mail_service = mail_service

  def test_email(self, user):
    print(user.email)
    self.__mail_service.send_mail(EmailTemplate.TEST, [user.email], None)