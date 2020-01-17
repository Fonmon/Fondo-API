from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from fondo_api.logic.activity_logic import *

class ActivityDetailView(APIView):

    def get(self, request, id):
        activity = get_activity(id)
        if activity is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(activity, status=status.HTTP_200_OK)

    def delete(self, request, id):
        remove_activity(id)
        return Response(status=status.HTTP_200_OK)

    def patch(self, request, id):
        patch = request.query_params.get('patch','activity')
        if patch != 'activity' and patch != 'user':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        activity = patch_activity(patch, id, request.data)
        if activity is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(activity, status=status.HTTP_200_OK)

class ActivityYearView(APIView):

    def get(self, request):
        years = get_years()
        if len(years) == 0:
            return Response(status = status.HTTP_204_NO_CONTENT)
        return Response(years,status=status.HTTP_200_OK)

    def post(self, request):
        state = create_year()
        if state:
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_304_NOT_MODIFIED)

class ActivityYearDetailView(APIView):

    def get(self, request, id_year):
        activities = get_activities(id_year)
        return Response(activities, status = status.HTTP_200_OK)

    def post(self, request, id_year):
        create_activity(request.data, id_year)
        return Response(status=status.HTTP_201_CREATED)