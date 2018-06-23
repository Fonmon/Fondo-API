from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser,JSONParser
from ..logic.user_logic import *

class UserView:
    @api_view(['GET','POST','PATCH'])
    @parser_classes((MultiPartParser,JSONParser))
    def view_get_post_users(request,format=None):
        if request.method =='POST':
            state, msg = create_user(request.data)
            if state:
                return Response(status = status.HTTP_201_CREATED)
            return Response({'message':msg},status = status.HTTP_409_CONFLICT)
        elif request.method == 'GET':
            page = int(request.query_params.get('page','1'))
            if page <= 0:
                return Response({'message':'Page number must be greater or equal than 0'},status = status.HTTP_400_BAD_REQUEST)
            return Response(get_users(page),status = status.HTTP_200_OK)
        else:
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
        elif request.method == 'DELETE':
            state = inactive_user(id)
            if state:
                return Response(status = status.HTTP_200_OK)
            return Response(status = status.HTTP_404_NOT_FOUND)
        else:
            state,code = update_user(id,request.data)
            if state:
                return Response(status = status.HTTP_200_OK)
            elif code == 404:
                return Response(status = status.HTTP_404_NOT_FOUND)
            elif code == 409:
                return Response(status = status.HTTP_409_CONFLICT)

    @api_view(['POST'])
    @permission_classes([])
    def view_activate_user(request,id):
        state = activate_user(id,request.data)
        if state:
            return Response(status = status.HTTP_200_OK)
        return Response(status = status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def view_logout(request):
        request.user.auth_token.delete()
        return Response(status = status.HTTP_200_OK)