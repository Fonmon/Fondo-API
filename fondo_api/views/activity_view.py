from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..logic.activity_logic import *

class ActivityView:
    @api_view(['GET','POST'])
    def view_get_post_years(request):
        if request.method == 'POST':
            state = create_year()
            if state:
                return Response(status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        else:
            years = get_years()
            if len(years) == 0:
                return Response(status = status.HTTP_204_NO_CONTENT)
            return Response(years,status=status.HTTP_200_OK)
    
    @api_view(['GET','POST'])
    def view_get_post_activities(request, id_year):
        if request.method == 'GET':
            activities = get_activities(id_year)
            return Response(activities, status = status.HTTP_200_OK)
        else:
            create_activity(request.data, id_year)
            return Response(status=status.HTTP_201_CREATED)
    
    @api_view(['GET','PATCH','DELETE'])
    def view_get_patch_delete_activity(request,id):
        if request.method == 'GET':
            activity = get_activity(id)
            if activity is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(activity, status = status.HTTP_200_OK)
        elif request.method == 'DELETE':
            remove_activity(id)
            return Response(status = status.HTTP_200_OK)
        else:
            patch = request.query_params.get('patch','activity')
            if patch != 'activity' and patch != 'user':
                return Response(status=status.HTTP_400_BAD_REQUEST)
            activity = patch_activity(patch, id, request.data)
            if activity is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(activity, status = status.HTTP_200_OK)