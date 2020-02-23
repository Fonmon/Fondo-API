import logging
from rest_framework.response import Response
from rest_framework.decorators import parser_classes
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from fondo_api.services.file import FileService

file_service = FileService()
logger = logging.getLogger(__name__)

class FileView(APIView):

    @parser_classes((MultiPartParser,))
    def post(self, request):
        try:
            if "name" in request.data and "file" in request.data and "type" in request.data:
                file_service.save_file(request.data)
                return Response(status=status.HTTP_201_CREATED)    
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            logger.error('Exception saving file: %s', exception)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        type = int(request.query_params.get('type', -1))
        files = file_service.get_files(type)
        return Response(files, status = status.HTTP_200_OK)

class FileDetailView(APIView):

    def get(self, request, id):
        url = file_service.get_signed_url(int(id))
        if url is not None:
            return Response(url, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)