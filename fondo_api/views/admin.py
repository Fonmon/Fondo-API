from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from fondo_api.services.mail import MailService
from fondo_api.services.admin import AdminService

mail_service = MailService()
admin_service = AdminService(mail_service)

class AdminView(APIView):
  def get(self, request):
    admin_service.test_email(request.user)
    return Response(status=status.HTTP_200_OK)
