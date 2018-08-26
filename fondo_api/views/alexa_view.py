from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..logic.alexa.amazon_alexa import AmazonAlexa
import logging, traceback

logger = logging.getLogger(__name__)
aws_alexa = AmazonAlexa()

class AlexaView(APIView):
    permission_classes = []

    def post(self,request):
        try:
            logger.info(request.body)
            logger.info(request.META.get('HTTP_SIGNATURECERTCHAINURL'))
            logger.info(request.META.get('HTTP_SIGNATURE'))

            aws_alexa.set_request(request)
            obj = aws_alexa.process()
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as exception:
            logger.error('Exception in Alexa: %s', exception)
            traceback.print_exc()
            if len(exception.args) == 2:
                type, message = exception.args
                switcher = {
                    400: status.HTTP_400_BAD_REQUEST,
                    401: status.HTTP_401_UNAUTHORIZED,
                    403: status.HTTP_403_FORBIDDEN,
                    405: status.HTTP_405_METHOD_NOT_ALLOWED,
                    422: status.HTTP_422_UNPROCESSABLE_ENTITY,
                    500: status.HTTP_500_INTERNAL_SERVER_ERROR
                }
                return Response(message, status=switcher.get(type, status.HTTP_400_BAD_REQUEST))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)