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
        return Response({'id': account_id}, status=status.HTTP_200_OK)

    def get(self, request):
        user = user_service.get_profile(request.user.id)

        all_accounts = (request.query_params.get('all_accounts') == 'true')
        state = int(request.query_params.get('state', 0))
        page = int(request.query_params.get('page', 1))
        paginate = True
        if request.query_params.get('paginate') is not None:
            paginate = (request.query_params.get('paginate') == 'true')
        if page <= 0:
            return Response({'message': 'Page number must be greater or equal than 0'}, status=status.HTTP_400_BAD_REQUEST)
        if state > 1 or state < 0:
            return Response({'message': 'State must be between 0 and 1'}, status=status.HTTP_400_BAD_REQUEST)
        if user.role <= 2:
            return Response(
                saving_account_service.get_accounts(user.id, page, all_accounts, state=state, paginate=paginate), 
                status=status.HTTP_200_OK
            )
        return Response(
            saving_account_service.get_accounts(user.id, page, state=state, paginate=paginate), 
            status=status.HTTP_200_OK
        )