from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser,JSONParser
from .logic.user_logic import *
from .logic.loan_logic import *
from .models import UserProfile

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
		page = int(request.query_params.get('page','1'))
		if page <= 0:
			return Response({'message':'Page number must be greater or equal than 0'},status = status.HTTP_400_BAD_REQUEST)
		if user.role <= 2:
			return Response(get_loans(user.id,page,all_loans),status.HTTP_200_OK)
		return Response(get_loans(user.id,page),status.HTTP_200_OK)
	if request.method == 'PATCH':
		bulk_update_loans(request.data)
		return Response(status=status.HTTP_200_OK)

# TODO: pagination
@api_view(['GET','POST','PATCH'])
@parser_classes((MultiPartParser,JSONParser))
def view_get_post_users(request,format=None):
	if request.method =='POST':
		state, msg = create_user(request.data)
		if state:
			return Response(status = status.HTTP_201_CREATED)
		return Response({'message':msg},status = status.HTTP_409_CONFLICT)
	if request.method == 'GET':
		page = int(request.query_params.get('page','1'))
		if page <= 0:
			return Response({'message':'Page number must be greater or equal than 0'},status = status.HTTP_400_BAD_REQUEST)
		return Response(get_users(page),status = status.HTTP_200_OK)
	if request.method == 'PATCH':
		bulk_update_users(request.data)
		return Response(status=status.HTTP_200_OK)

@api_view(['GET','PATCH','DELETE'])
def view_get_update_delete_user(request,id):
	id = int(id);
	if request.method == 'GET':
		if id == -1:
			id = request.user.id
		state, data = get_user(id)
		if state:
			return Response(data,status = status.HTTP_200_OK)
		return Response(status = status.HTTP_404_NOT_FOUND)
	if request.method == 'DELETE':
		state = inactive_user(id)
		if state:
			return Response(status = status.HTTP_200_OK)
		return Response(status = status.HTTP_404_NOT_FOUND)
	if request.method == 'PATCH':
		state,code = update_user(id,request.data)
		if state:
			return Response(status = status.HTTP_200_OK)
		elif code == 404:
			return Response(status = status.HTTP_404_NOT_FOUND)
		elif code == 409:
			return Response(status = status.HTTP_409_CONFLICT)

@api_view(['POST'])
def view_logout(request):
	if request.method == 'POST':
		request.user.auth_token.delete()
		return Response(status = status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([])
def view_activate_user(request,id):
	if request.method == 'POST':
		state = activate_user(id,request.data)
		if state:
			return Response(status = status.HTTP_200_OK)
		return Response(status = status.HTTP_404_NOT_FOUND)

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