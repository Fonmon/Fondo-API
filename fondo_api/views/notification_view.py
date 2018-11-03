from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..logic.notifications_logic import *

class NotificationView:

    @api_view(['POST'])
    def view_notification_subscribe(request):
        print(request.data)
        state = save_subscription(request.user.id, request.data)
        if state == 200:
            return Response(status = status.HTTP_200_OK)
        elif state == 500:
            return Response(status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status = status.HTTP_404_NOT_FOUND)

    @api_view(['POST'])
    def view_notification_unsubscribe(request):
        print(request.data)
        state = unregister_subscription(request.user.id, request.data)
        if state == 200:
            return Response(status = status.HTTP_200_OK)
        return Response(status = status.HTTP_404_NOT_FOUND)