import json
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal

from fondo_api.models import * 

class AbstractTest(TestCase):
    # initialize the APIClient app
    client = Client()
    THREEPLACES = Decimal(10) ** -3

    def create_user(self):
        user = UserProfile.objects.create_user(
            id = 1,
            first_name = 'Foo Name',
            last_name = 'Foo Last Name',
            identification = 99999,
            role = 0,
            username = "mail_for_tests@mail.com",
            email = "mail_for_tests@mail.com",
            password = "password"
        )
        UserFinance.objects.create(
            contributions= 2000,
            balance_contributions= 2000,
            total_quota= 1000,
            available_quota= 500,
            user= user
        )
        UserPreference.objects.create( user = user)

    def get_token(self,username, password):
        body = {
            'username':'{}'.format(username),
            'password':'{}'.format(password)
        }
        response = self.client.post(
            reverse('obtain_auth_token'),
            data = json.dumps(body),
            content_type='application/json',
        )
        return response.data['token']

    def get_auth_header(self,token):
        return {'HTTP_AUTHORIZATION': "Token {}".format(token)}