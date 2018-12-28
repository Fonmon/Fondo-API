from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from fondo_api.logic.notifications_logic import *

class NotificationView:

    @api_view(['POST'])
    def view_notification_subscribe(request):
        save_subscription(request.user.id, request.data)
        return Response(status = status.HTTP_200_OK)

    @api_view(['POST'])
    def view_notification_unsubscribe(request):
        state = unregister_subscription(request.user.id, request.data)
        if state == 200:
            return Response(status = status.HTTP_200_OK)
        return Response(status = status.HTTP_404_NOT_FOUND)