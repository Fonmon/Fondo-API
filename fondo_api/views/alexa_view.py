from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..logic.alexa.amazon_alexa import AmazonAlexa
import logging

logger = logging.getLogger(__name__)

class AlexaView(APIView):
    permission_classes = []
    
    def __init__(self):
        self.aws_alexa = AmazonAlexa()

    def post(self,request):
        try:
            logger.info('Alexa signature url: %s',request.META.get('HTTP_SIGNATURECERTCHAINURL'))
            logger.info('Alexa signature: %s',request.META.get('HTTP_SIGNATURE'))

            self.aws_alexa.set_request(request)
            response = self.aws_alexa.process()
            return Response(response, status=status.HTTP_200_OK)
        except Exception as exception:
            type, message = exception.args
            switcher = {
                400: status.HTTP_400_BAD_REQUEST,
                403: status.HTTP_403_FORBIDDEN,
                422: status.HTTP_422_UNPROCESSABLE_ENTITY,
                500: status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(message, status=switcher.get(type, status.HTTP_400_BAD_REQUEST))