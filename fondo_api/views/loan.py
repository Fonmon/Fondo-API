from rest_framework.decorators import parser_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from datetime import datetime

from fondo_api.services.loan import LoanService
from fondo_api.services.notification import NotificationService
from fondo_api.services.user import UserService

notification_service = NotificationService()
user_service = UserService()
loan_service = LoanService(user_service, notification_service)

class LoanView(APIView):

    def get(self, request):
        user = user_service.get_profile(request.user.id)

        all_loans = (request.query_params.get('all_loans') == 'true')
        state = int(request.query_params.get('state', 4))
        page = int(request.query_params.get('page', '1'))
        paginate = True
        if request.query_params.get('paginate') is not None:
            paginate = (request.query_params.get('paginate') == 'true')
        if page <= 0:
            return Response({'message': 'Page number must be greater or equal than 0'}, status=status.HTTP_400_BAD_REQUEST)
        if state > 4 or state < 0:
            return Response({'message': 'State must be between 0 and 4'}, status=status.HTTP_400_BAD_REQUEST)
        if user.role <= 2:
            return Response(
                loan_service.get_loans(user.id, page, all_loans, state=state, paginate=paginate), 
                status=status.HTTP_200_OK
            )
        return Response(
            loan_service.get_loans(user.id, page, state=state, paginate=paginate), 
            status=status.HTTP_200_OK
        )

    def post(self, request):
        user = user_service.get_profile(request.user.id)

        state, msg = loan_service.create_loan(user.id, request.data)
        if state:
            return Response({'id': msg}, status=status.HTTP_201_CREATED)
        return Response({'message': msg}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @parser_classes((MultiPartParser,))
    def patch(self, request):
        loan_service.bulk_update_loans(request.data)
        return Response(status=status.HTTP_200_OK)

class LoanDetailView(APIView):

    def get(self, request, id):
        state, data = loan_service.get_loan(id)
        if state:
            return Response(data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, id):
        new_state = int(request.data['state'])
        if new_state <= 3:
            state, msg = loan_service.update_loan(id, new_state)
            if state:
                return Response(msg, status=status.HTTP_200_OK)
            return Response({'message': msg}, status.HTTP_404_NOT_FOUND)
        return Response({'message': 'State must be less or equal than 3'}, status=status.HTTP_400_BAD_REQUEST)

class LoanAppsView(APIView):

    def post(self, request, id, app):
        if app == 'paymentProjection':
            if 'to_date' not in request.data:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            try:
                to_date = datetime.strptime(request.data['to_date'], '%Y-%m-%d').date()
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            response = loan_service.payment_projection(id, to_date)
            if response is not None:
                return Response(response, status=status.HTTP_200_OK)
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        if app == 'refinance':
            response = loan_service.refinance_loan(id, request.data, request.user.id)
            if response is not None:
                return Response({'id': response}, status=status.HTTP_200_OK)
            return Response(status=tatus.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)