from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from .logic.user_logic import *
from .models import Loan as LoanModel
from .serializers import *

import json

@api_view(['GET'])
def get_loans(request,pk):
	try:
		loans = LoanModel.objects.filter(user_id = pk)
	except LoanModel.DoesNotExist:
		return Response(status = status.HTTP_404_NOT_FOUND)

	if request.method == 'GET':
		return Response({'loans':len(loans)})

@api_view(['POST'])
def post_loan(request):
	if request.method == 'POST':
		return Response({})

@api_view(['GET','POST'])
def get_post_user(request):
	if request.method =='POST':
		body_content = json.loads(request.body)
		state, msg = create_user(body_content)
		if state:
			return Response(status = status.HTTP_201_CREATED)
		return Response({'message':msg},status = status.HTTP_409_CONFLICT);


#http://blog.apcelent.com/django-json-web-token-authentication-backend.html
'''from django.contrib.auth.hashers import make_password
@api_view(['POST'])
@permission_classes([])
def obtain_auth_token(request):
	body = json.loads(request.body)
	allPwd = body['email']+body['password']
	password = make_password(allPwd)
	return Response({'username1':body['email'],'password1':password})
'''