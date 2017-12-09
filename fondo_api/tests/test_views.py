import json
import base64
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import *
from ..serializers import *

# initialize the APIClient app
client = Client()

def create_user():
	user = User.objects.create(
		full_name = 'Foo Full Name',
		identification = 99999
	)
	UserAuth.objects.create(
		email = "mail_for_tests@mail.com",
		password = "pbkdf2_sha256$100000$iGqql2jYhn1b$gik5vcbaSyLZZyFFsU12Pk5TfN8GtR8rXPdCqZPMR3c=",
		is_active = True,
		user = user
	)

def get_auth_header():
	return {'HTTP_AUTHORIZATION': "Basic bWFpbF9mb3JfdGVzdHNAbWFpbC5jb206cGFzc3dvcmQ="}

class UserViewTest(TestCase):

	def setUp(self):
		create_user()
		self.object_json = {
			'full_name': 'Foo Name',
			'identification': 123,
			'email': 'mail@mail.com',
			'role': 2
		}

		self.object_json_identification_r = {
			'full_name': 'Foo Name 2',
			'identification': 99999,
			'email': 'mail2@mail.com',
			'role': 2
		}

		self.object_json_email_r = {
			'full_name': 'Foo Name 3',
			'identification': 1234,
			'email': 'mail_for_tests@mail.com',
			'role': 2
		}

	def test_success_post(self):
		response = client.post(
			reverse('get_post_user'),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**get_auth_header()
		)
		self.assertEquals(response.status_code,status.HTTP_201_CREATED)

	def test_unsuccess_post_identification(self):
		response = client.post(
			reverse('get_post_user'),
			data = json.dumps(self.object_json_identification_r),
			content_type='application/json',
			**get_auth_header()
		)
		self.assertEquals(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEquals(response.data['message'],'Identification already exists')

	def test_unsuccess_post_email(self):
		response = client.post(
			reverse('get_post_user'),
			data = json.dumps(self.object_json_email_r),
			content_type='application/json',
			**get_auth_header()
		)
		self.assertEquals(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEquals(response.data['message'],'Email already exists')