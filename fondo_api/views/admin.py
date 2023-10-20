from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from fondo_api.services.mail import MailService
from fondo_api.services.admin import AdminService
from fondo_api.services.notification import NotificationService

mail_service = MailService()
notification_service = NotificationService()
admin_service = AdminService(mail_service, notification_service)

class AdminView(APIView):
  def get(self, request):
    type = request.query_params.get('type', None)
    if type == 'email':
      admin_service.test_email(request.user)
    if type == 'notifications':
      admin_service.test_notifications(request.user)
    if type == None:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)
