from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from fondo_api.services.mail import MailService
from fondo_api.enums import EmailTemplate

mail_service = MailService()

class TmpView(APIView):
  permission_classes = []
  
  def get(self, request, path):
    mail_service.send_mail(
      EmailTemplate.TMP,
      [
        'erikita_2605@hotmail.com',
        'jcmendezo905@gmail.com'
      ],
      {
        'path': path,
      },
      ['cmiguelmg@gmail.com']
    )
    return Response(status=status.HTTP_201_CREATED)