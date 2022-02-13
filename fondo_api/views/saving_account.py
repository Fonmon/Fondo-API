from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from fondo_api.services.user import UserService
from fondo_api.services.saving_account import SavingAccountService

saving_account_service = SavingAccountService()
user_service = UserService()

class SavingAccountView(APIView):

    def post(self, request):
        account_id = saving_account_service.create_account(request.user.id, request.data)
        return Response(account_id, status=status.HTTP_200_OK)

    def get(self, request):
        return Response({}, status=status.HTTP_200_OK)