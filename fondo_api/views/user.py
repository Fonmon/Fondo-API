import logging
from rest_framework.decorators import parser_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from fondo_api.services.user import UserService
from fondo_api.services.notification import NotificationService
from fondo_api.services.mail import MailService

notification_service = NotificationService()
mail_service = MailService()
user_service = UserService(notification_service, mail_service)
logger = logging.getLogger(__name__)

class UserView(APIView):

    def post(self, request):
        state, msg = user_service.create_user(request.data)
        if state:
            return Response(status=status.HTTP_201_CREATED)
        return Response({'message': msg}, status=status.HTTP_409_CONFLICT)

    def get(self, request):
        page = None
        if request.query_params.get('page') is not None:
            page = int(request.query_params.get('page', '1'))
        if page is not None and page <= 0:
            return Response(
                {'message': 'Page number must be greater than 0'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(user_service.get_users(page), status=status.HTTP_200_OK)

    @parser_classes((MultiPartParser,))
    def patch(self, request):
        user_service.bulk_update_users(request.data)
        return Response(status=status.HTTP_200_OK)

class UserDetailView(APIView):

    def get(self, request, id):
        id = int(id)
        if id == -1:
            id = request.user.id
        state, data = user_service.get_user(id)
        if state:
            return Response(data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, id):
        id = int(id)
        state, code = user_service.update_user(id, request.data)
        if state:
            return Response(status=status.HTTP_200_OK)
        elif code == 404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_409_CONFLICT)

    def delete(self, request, id):
        id = int(id)
        state = user_service.inactive_user(id)
        if state:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)            

class UserActivateView(APIView):
    permission_classes = []

    def post(self, request, id):
        state = user_service.activate_user(id, request.data)
        if state:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

class UserAppsView(APIView):

    def post(self, request, app):
        try:
            if app == "birthdates":
                return Response(user_service.get_users_birthdate(), status=status.HTTP_200_OK)
        except Exception as exception:
            logger.error('Exception executing an user app: %s', exception)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)