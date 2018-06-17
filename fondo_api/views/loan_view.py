from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser,JSONParser
from datetime import datetime
from ..logic.loan_logic import *

class LoanView:
	@api_view(['POST'])
	def view_loan_apps(request,id,app):
		if app == 'paymentProjection':
			if 'to_date' not in request.data:
				return Response(status = status.HTTP_400_BAD_REQUEST)
			to_date = datetime.strptime(request.data['to_date'],'%Y-%m-%d').date()
			return Response(payment_projection(id,to_date),status = status.HTTP_200_OK)
		return Response(status = status.HTTP_404_NOT_FOUND)

	@api_view(['GET','PATCH'])
	def view_get_update_loan(request,id):
		if request.method == 'PATCH':
			new_state = int(request.data['state'])
			if new_state <= 3:
				state, msg = update_loan(id,new_state)
				if state:
					return Response(msg,status=status.HTTP_200_OK)
				return Response({'message':msg},status.HTTP_404_NOT_FOUND)
			return Response({'message':'State must be less or equal than 3'},status = status.HTTP_400_BAD_REQUEST)
		if request.method == 'GET':
			state, data = get_loan(id)
			if state:
				return Response(data,status = status.HTTP_200_OK)
			return Response(status = status.HTTP_404_NOT_FOUND)

	@api_view(['GET','POST','PATCH'])
	@parser_classes((MultiPartParser,JSONParser))
	def view_get_post_loans(request):
		user = UserProfile.objects.get(id = request.user.id)
		if request.method == 'POST':
			state, msg = create_loan(user.id,request.data)
			if state:
				return Response({'id':msg},status = status.HTTP_201_CREATED)
			return Response({'message':msg},status = status.HTTP_406_NOT_ACCEPTABLE)
		if request.method == 'GET':
			all_loans = (request.query_params.get('all_loans') == 'true')
			state = int(request.query_params.get('state',4))
			page = int(request.query_params.get('page','1'))
			paginate = True
			if request.query_params.get('paginate') is not None:
				paginate = (request.query_params.get('paginate') == 'true')
			if page <= 0:
				return Response({'message':'Page number must be greater or equal than 0'},status = status.HTTP_400_BAD_REQUEST)
			if state > 4 or state < 0:
				return Response({'message':'State must be between 0 and 4'},status = status.HTTP_400_BAD_REQUEST)
			if user.role <= 2:
				return Response(get_loans(user.id,page,all_loans,state=state,paginate=paginate),status.HTTP_200_OK)
			return Response(get_loans(user.id,page,state=state,paginate=paginate),status.HTTP_200_OK)
		if request.method == 'PATCH':
			bulk_update_loans(request.data)
			return Response(status=status.HTTP_200_OK)