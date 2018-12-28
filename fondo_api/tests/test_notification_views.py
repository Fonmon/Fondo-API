import json
from django.urls import reverse
from mock import patch
from rest_framework import status

from fondo_api.tests.abstract_test import AbstractTest
from fondo_api.models import *
from fondo_api.logic.notifications_logic import send_notification

view_notification_subscribe = 'view_notification_subscribe'
view_notification_unsubscribe = 'view_notification_unsubscribe'

class NotificationViewTest(AbstractTest):
    def setUp(self):
        self.create_user()
        self.token = self.get_token('mail_for_tests@mail.com','password')
        self.subscription_json = {
            'endpoint': 'https://fcm.googleapis.com/fcm/send/eX6bP7wJrF4:APA91bG3MLpEG28xFOuYLQc-AB78XRywxVFOtGQpGwUQp5NWc-6GYzjvgSdCIiI4U_cFsS22Qi9QPpdI3hZ1OjyO8LcAoSfmhnK31IaXJc7OhnaauHzToLZt7HpP9bZO59yIP8i5FWs5', 
            'expirationTime': None, 
            'keys': {
                'p256dh': 'BHUdL9eM2s6BoDOIl0zz68ZsPqY9wLAQC8CttBykmgZC1SU3U7wV6tKcJ4wjkj1-T_0qrsOqjzBmTcxvhUPilA4', 
                'auth': '60-ComhtIqES-C7GmbrDVg'
            }
        }
        self.subscription_not_exist = {
            'endpoint': 'https://fcm.googleapis.com/fcm/send/eX6bP7wJrF4:APA91bG3FOuYLQc-AB78XRywxVFOtGQpGwUQp5NWc-6GYzjvgSdCIiI4U_cFsS22Qi9QPpdI3hZ1OjyO8LcAoSfmhnK31IaXJc7OhnaauHzToLZt7HpP9bZO59yIP8i5FWs5', 
            'expirationTime': None, 
            'keys': {
                'p256dh': 'BHUdL9eM2s6BoDOIl0zz68ZsPqY9wLAQC8CttBykmgZC1SU3U7wV6tKcJ4wjkj1-T_0qrsOqjzBmTcxvhUPilA4', 
                'auth': '60-ComhtIqES-C7GmbrDVg'
            }
        }

    def test_subscribe(self):
        response = self.client.post(
            reverse(view_notification_subscribe),
            data = json.dumps(self.subscription_json),
            content_type='application/json',
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(NotificationSubscriptions.objects.all()), 1)

    def test_unsubscribe(self):
        response = self.client.post(
            reverse(view_notification_subscribe),
            data = json.dumps(self.subscription_json),
            content_type='application/json',
            **self.get_auth_header(self.token)
        )

        response = self.client.post(
            reverse(view_notification_unsubscribe),
            data = json.dumps(self.subscription_json),
            content_type='application/json',
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(NotificationSubscriptions.objects.all()), 0)

    def test_unsubscribe_not_found(self):
        response = self.client.post(
            reverse(view_notification_subscribe),
            data = json.dumps(self.subscription_json),
            content_type='application/json',
            **self.get_auth_header(self.token)
        )

        response = self.client.post(
            reverse(view_notification_unsubscribe),
            data = json.dumps(self.subscription_not_exist),
            content_type='application/json',
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

    @patch('requests.post',return_value=False)
    def pending_test_send_notification(self, mock):
        response = self.client.post(
            reverse(view_notification_subscribe),
            data = json.dumps(self.subscription_json),
            content_type='application/json',
            **self.get_auth_header(self.token)
        )
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(NotificationSubscriptions.objects.all()), 1)

        send_notification([1], 'Test Notification Message')