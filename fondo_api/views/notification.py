from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from fondo_api.services.notification import NotificationService

notification_service = NotificationService()

class NotificationView(APIView):

    def post(self, request, operation):
        if operation == 'subscribe':
            notification_service.save_subscription(request.user.id, request.data)
            return Response(status=status.HTTP_200_OK)
        elif operation == 'unsubscribe':
            state = notification_service.unregister_subscription(request.user.id, request.data)
            if state == 200:
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)