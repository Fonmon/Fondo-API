import gspread
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from babel.dates import format_datetime
from django.conf import settings

class TmpView(APIView):
  permission_classes = []
  
  def __init__(self):
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', None)
    self.client = gspread.service_account(filename=credentials_path)

  def get(self, request):
    now = timezone.now()
    date = format_datetime(now, locale=settings.LANGUAGE_LOCALE)
    perfil_politico = request.query_params.get('perfil_politico', None)
    contexto_laboral = request.query_params.get('contexto_laboral', None)
    candidato_alineado = request.query_params.get('candidato_alineado', None)
    voto_declarado = request.query_params.get('voto_declarado', None)
    sheet = self.client.open("resultados encuesta 2026").sheet1
    sheet.append_row([date, perfil_politico, contexto_laboral, candidato_alineado, voto_declarado])
    return Response(status=status.HTTP_201_CREATED)