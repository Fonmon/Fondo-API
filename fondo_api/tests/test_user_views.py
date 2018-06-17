import json
from .abstract_test import AbstractTest
from mock import patch
from django.urls import reverse
from django.test.client import encode_multipart
from rest_framework import status
from ..models import *
from django.core import mail

view_get_post_users = 'view_get_post_users'
view_get_update_delete_user = 'view_get_update_delete_user'
view_activate_user = 'view_activate_user'
view_logout = 'view_logout'

class UserViewTest(AbstractTest):
	def setUp(self):
		self.create_user()
		self.token = self.get_token('mail_for_tests@mail.com','password')
		self.object_json = {
			'first_name': 'Foo Name',
			'last_name': 'Last Name',
			'identification': 123,
			'email': 'mail@mail.com',
			'username': 'mail@mail.com',
			'role': 2
		}

		self.object_json_identification_r = {
			'first_name': 'Foo Name 2',
			'last_name': 'Last Name 2',
			'identification': 99999,
			'email': 'mail2@mail.com',
			'username': 'mail2@mail.com',
			'role': 2
		}

		self.object_json_email_r = {
			'first_name': 'Foo Name 3',
			'last_name': 'Last Name 3',
			'identification': 1234,
			'email': 'mail_for_tests@mail.com',
			'username': 'mail_for_tests@mail.com',
			'role': 2
		}

		self.object_json_user_update = {
			'identification':123,
			'first_name': 'Foo Name update',
			'last_name': 'Last Name update',
			'email': 'mail_updated@mail.com2',
			'role': 2,
			'contributions': 2000,
			'balance_contributions': 2000,
			'total_quota': 1000,
			'utilized_quota': 500
		}

		self.object_json_user_update_same_finance = {
			'contributions': 2000,
			'balance_contributions': 2000,
			'total_quota':1000,
			'available_quota': 500,
			'utilized_quota':0,
			'identification':123,
			'first_name': 'Foo Name update',
			'last_name': 'Last Name update',
			'email': 'mail_updated@mail.com2',
			'role': 2,
		}

		self.object_json_user_update_email_r = {
			'identification':12312451241243,
			'first_name': 'Foo Name update',
			'last_name': 'Last Name update',
			'email': 'mail@mail.com',
			'role': 2,
			'contributions': 2000,
			'balance_contributions': 2000,
			'total_quota': 1000,
			'utilized_quota': 500
		}

		self.object_json_user_update_identification_r = {
			'identification':123,
			'first_name': 'Foo Name update',
			'last_name': 'Last Name update',
			'email': 'mail2@m2ail.com',
			'role': 2,
			'contributions': 2000,
			'balance_contributions': 2000,
			'total_quota': 1000,
			'utilized_quota': 500
		}

	def test_success_post(self):
		response = self.client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_201_CREATED)

		user = UserProfile.objects.get(identification = 123)
		self.assertEquals(user.first_name,'Foo Name')
		self.assertEquals(user.identification,123)

		self.assertEquals(user.email, "mail@mail.com")
		self.assertEquals(user.role, 2)
		self.assertEquals(user.get_role_display(),'TREASURER')
		self.assertIsNotNone(user.key_activation)
		self.assertFalse(user.is_active)

		self.assertEquals(len(mail.outbox),1)
		self.assertEquals(mail.outbox[0].subject,'[Fondo Montañez] Activación de cuenta')
		self.assertEquals(len(mail.outbox[0].to),1)
		self.assertEquals(mail.outbox[0].to[0],'mail@mail.com')

		self.assertEquals(len(UserProfile.objects.all()),2)
		self.assertEquals(len(UserFinance.objects.all()),2)

	@patch('fondo_api.logic.sender_mails.send_activation_mail',return_value=False)
	def test_invalid_email(self,mock):
		response = self.client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEquals(response.data['message'],'Invalid email')

		self.assertEquals(len(UserProfile.objects.all()),1)
		self.assertEquals(len(UserFinance.objects.all()),1)

	def test_unsuccess_post_identification(self):
		response = self.client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json_identification_r),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEquals(response.data['message'],'Identification/email already exists')

		self.assertEquals(len(UserProfile.objects.all()),1)
		self.assertEquals(len(UserFinance.objects.all()),1)

	def test_unsuccess_post_email(self):
		response = self.client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json_email_r),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEquals(response.data['message'],'Identification/email already exists')

		self.assertEquals(len(UserProfile.objects.all()),1)
		self.assertEquals(len(UserFinance.objects.all()),1)

	def test_get_users(self):
		response = self.client.get(
			reverse(view_get_post_users),
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),len(UserProfile.objects.filter(is_active=True)))
		for user in response.data['list']:
			self.assertIsNotNone(user['id'])
			self.assertIsNotNone(user['identification'])
			self.assertIsNotNone(user['full_name'])
			self.assertIsNotNone(user['email'])
			self.assertIsNotNone(user['role'])

	def test_get_users_empty(self):
		response = self.client.get(
			"%s?page=2" % reverse(view_get_post_users),
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),0)
		self.assertEquals(response.data['num_pages'],1)

	def test_get_users_error_pagination(self):
		response = self.client.get(
			"%s?page=0" % reverse(view_get_post_users),
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEquals(response.data['message'],'Page number must be greater or equal than 0')

	def test_get_user(self):
		response = self.client.get(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		self.assertEquals(response.data['id'],1)
		self.assertEquals(response.data['identification'],99999)
		self.assertEquals(response.data['first_name'],'Foo Name')
		self.assertEquals(response.data['last_name'],'Foo Last Name')
		self.assertEquals(response.data['email'],'mail_for_tests@mail.com')
		self.assertEquals(response.data['role'],0)
		self.assertEquals(response.data['contributions'],2000)
		self.assertEquals(response.data['balance_contributions'],2000)
		self.assertEquals(response.data['total_quota'],1000)
		self.assertEquals(response.data['available_quota'],500)
		self.assertEquals(response.data['utilized_quota'],0)

	def test_get_session_user(self):
		response = self.client.get(
			reverse(view_get_update_delete_user,kwargs={'id': -1}),
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		self.assertEquals(response.data['id'],1)
		self.assertEquals(response.data['identification'],99999)
		self.assertEquals(response.data['first_name'],'Foo Name')
		self.assertEquals(response.data['last_name'],'Foo Last Name')
		self.assertEquals(response.data['email'],'mail_for_tests@mail.com')
		self.assertEquals(response.data['role'],0)
		self.assertEquals(response.data['contributions'],2000)
		self.assertEquals(response.data['balance_contributions'],2000)
		self.assertEquals(response.data['total_quota'],1000)
		self.assertEquals(response.data['available_quota'],500)
		self.assertEquals(response.data['utilized_quota'],0)

	def test_get_user_not_found(self):
		response = self.client.get(
			reverse(view_get_update_delete_user,kwargs={'id': 2}),
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_delete_user(self):
		response = self.client.delete(
			reverse(view_get_update_delete_user,kwargs={'id': 2}),
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

		response = self.client.delete(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		user = User.objects.get(id = 1)
		self.assertFalse(user.is_active)

		response = self.client.get(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_401_UNAUTHORIZED)
		try:
			self.get_token('mail_for_tests@mail.com','password')
			self.fail('That account is inactive')
		except KeyError:
			pass

	def test_patch_user(self):
		response = self.client.patch(
			reverse(view_get_update_delete_user,kwargs={'id': 2}),
			data=json.dumps(self.object_json_user_update),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

		response = self.client.patch(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)

		user = UserProfile.objects.get(id=1)
		self.assertEquals(user.first_name,'Foo Name update')
		self.assertEquals(user.last_name,'Last Name update')
		self.assertEquals(user.email,'mail_updated@mail.com2')
		self.assertEquals(user.username,'mail_updated@mail.com2')

	def test_patch_user_not_finance(self):
		response = self.client.patch(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update_same_finance),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)

		user = UserProfile.objects.get(id=1)
		self.assertEquals(user.first_name,'Foo Name update')
		self.assertEquals(user.last_name,'Last Name update')
		self.assertEquals(user.email,'mail_updated@mail.com2')
		self.assertEquals(user.username,'mail_updated@mail.com2')

	def test_patch_user_conflict(self):
		response = self.client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_201_CREATED)
		self.assertEquals(len(mail.outbox),1)
		self.assertEquals(mail.outbox[0].subject,'[Fondo Montañez] Activación de cuenta')
		self.assertEquals(len(mail.outbox[0].to),1)
		self.assertEquals(mail.outbox[0].to[0],'mail@mail.com')

		response = self.client.patch(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update_identification_r),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_409_CONFLICT)

		response = self.client.patch(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update_email_r),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_409_CONFLICT)

	def test_activation_successful(self):
		response = self.client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_201_CREATED)
		self.assertEquals(len(mail.outbox),1)
		self.assertEquals(mail.outbox[0].subject,'[Fondo Montañez] Activación de cuenta')
		self.assertEquals(len(mail.outbox[0].to),1)
		self.assertEquals(mail.outbox[0].to[0],'mail@mail.com')

		user = UserProfile.objects.get(identification = 123)
		obj = {
			'password':'newPassword123',
			'identification':123,
			'key':user.key_activation
		};

		response = self.client.post(
			reverse(view_activate_user,kwargs={'id': user.id}),
			data = json.dumps(obj),
			content_type='application/json',
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)

		user = UserProfile.objects.get(identification = 123)
		self.assertEquals(user.is_active,True)
		self.assertTrue('pbkdf2_sha256' in user.password)

	def test_activation_unsuccessful(self):
		response = self.client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_201_CREATED)
		self.assertEquals(len(mail.outbox),1)
		self.assertEquals(mail.outbox[0].subject,'[Fondo Montañez] Activación de cuenta')
		self.assertEquals(len(mail.outbox[0].to),1)
		self.assertEquals(mail.outbox[0].to[0],'mail@mail.com')

		user = UserProfile.objects.get(identification = 123)
		obj = {
			'password':'newPassword123',
			'identification':1234,
			'key':user.key_activation
		};

		response = self.client.post(
			reverse(view_activate_user,kwargs={'id': user.id}),
			data = json.dumps(obj),
			content_type='application/json',
		)
		self.assertEquals(response.status_code,status.HTTP_404_NOT_FOUND)

		user = UserProfile.objects.get(identification = 123)
		self.assertEquals(user.is_active,False)
		self.assertFalse('pbkdf2_sha256' in user.password)

	def test_logout(self):
		response = self.client.post(
			reverse(view_logout),
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		response = self.client.post(
			reverse(view_logout),
			**self.get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_401_UNAUTHORIZED)

	def create_test_file(self):
		try:
			file = open("testfile.txt","w")
			file.write("1\t100\t1000\t200\t300\r\n")
			file.write("2\t400\t1000\t500\t600\r\n")
			file.write("3\t700\t1000\t800\t900\r\n")
			file.write("4\t0\t0\t0\t0\r\n")
		finally:
			file.close()
		return file

	def test_bulk_update_users(self):
		for i in range(3):
			user = UserProfile.objects.create_user(
				id=i+5,
				first_name = 'Foo Name',
				last_name = 'Foo Last Name',
				identification = i+1,
				username = "mail{}@mail.com".format(i+1),
				email = "mail{}@mail.com".format(i+1),
				password = "password"
			)
			UserFinance.objects.create(
				contributions= 0,
				balance_contributions= 0,
				total_quota= 0,
				available_quota= 0,
				utilized_quota=0,
				user= user
			)
		file = {}
		created_file = self.create_test_file()
		file_reader = open(created_file.name,'r')
		file['file'] = file_reader
		response = self.client.patch(
			reverse(view_get_post_users),
			data=encode_multipart('file',file),
			content_type='multipart/form-data; boundary=file',
			**self.get_auth_header(self.token)
		)

		self.assertEquals(response.status_code,status.HTTP_200_OK)

		user_finance = UserFinance.objects.get(user_id=5)
		self.assertEquals(user_finance.balance_contributions,100)
		self.assertEquals(user_finance.total_quota,1000)
		self.assertEquals(user_finance.contributions,200)
		self.assertEquals(user_finance.utilized_quota,300)
		self.assertEquals(user_finance.available_quota,700)

		user_finance = UserFinance.objects.get(user_id=6)
		self.assertEquals(user_finance.balance_contributions,400)
		self.assertEquals(user_finance.total_quota,1000)
		self.assertEquals(user_finance.contributions,500)
		self.assertEquals(user_finance.utilized_quota,600)
		self.assertEquals(user_finance.available_quota,400)

		user_finance = UserFinance.objects.get(user_id=7)
		self.assertEquals(user_finance.balance_contributions,700)
		self.assertEquals(user_finance.total_quota,1000)
		self.assertEquals(user_finance.contributions,800)
		self.assertEquals(user_finance.utilized_quota,900)
		self.assertEquals(user_finance.available_quota,100)