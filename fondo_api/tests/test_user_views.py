import json
from mock import patch
from django.urls import reverse
from django.test.client import encode_multipart
from rest_framework import status
from django.core import mail

from fondo_api.models import *
from fondo_api.tests.abstract_test import AbstractTest
from fondo_api.services.mail import MailService
from fondo_api.enums import EmailTemplate

view_user = 'view_user'
view_user_detail = 'view_user_detail'
view_user_activate = 'view_user_activate'
view_user_apps = 'view_user_apps'

class UserViewTest(AbstractTest):
	def setUp(self):
		self.create_user()
		self.create_basic_users();
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
			'personal': {
				'identification':123,
				'first_name': 'Foo Name update',
				'last_name': 'Last Name update',
				'email': 'mail_updated@mail.com2',
				'role': 2,
				'birthdate': '1995-11-07'
			},
			'finance': {
				'contributions': 2000,
				'balance_contributions': 2000,
				'total_quota': 1000,
				'utilized_quota': 500
			}
		}

		self.object_json_user_update_same_finance = {
			'finance': {
				'contributions': 2000,
				'balance_contributions': 2000,
				'total_quota':1000,
				'available_quota': 500,
				'utilized_quota':0
			},
			'personal': {
				'identification':123,
				'first_name': 'Foo Name update',
				'last_name': 'Last Name update',
				'email': 'mail_updated@mail.com2',
				'role': 2,
			}
		}

		self.object_json_user_update_email_r = {
			'personal': {
				'identification':12312451241243,
				'first_name': 'Foo Name update',
				'last_name': 'Last Name update',
				'email': 'mail@mail.com',
				'role': 2
			},
			'finance': {
				'contributions': 2000,
				'balance_contributions': 2000,
				'total_quota': 1000,
				'utilized_quota': 500
			}
		}

		self.object_json_user_update_identification_r = {
			'personal': {
				'identification':123,
				'first_name': 'Foo Name update',
				'last_name': 'Last Name update',
				'email': 'mail2@m2ail.com',
				'role': 2
			},
			'finance': {
				'contributions': 2000,
				'balance_contributions': 2000,
				'total_quota': 1000,
				'utilized_quota': 500
			}
		}

	@patch.object(MailService, 'send_mail')
	def test_success_post(self, mock):
		response = self.client.post(
			reverse(view_user),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_201_CREATED)

		user = UserProfile.objects.get(identification = 123)
		self.assertEqual(user.first_name,'Foo Name')
		self.assertEqual(user.identification,123)

		self.assertEqual(user.email, "mail@mail.com")
		self.assertEqual(user.role, 2)
		self.assertEqual(user.get_role_display(),'TREASURER')
		self.assertIsNotNone(user.key_activation)
		self.assertFalse(user.is_active)

		self.assertTrue(mock.called)
		mock.assert_called_once_with(EmailTemplate.USER_ACTIVATION, [user.email], {
			'user_full_name': '{} {}'.format(user.first_name, user.last_name),
			'user_id': user.id,
			'user_key': user.key_activation,
			'host_url': 'http://localhost:3000'
		})

		self.assertEqual(len(UserProfile.objects.all()), 12)
		self.assertEqual(len(UserFinance.objects.all()), 12)

	@patch.object(MailService, 'send_mail', return_value=False)
	def test_invalid_email(self,mock):
		response = self.client.post(
			reverse(view_user),
			data = json.dumps(self.object_json),
			content_type = 'application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
		self.assertEqual(response.data['message'], 'Invalid email')

		self.assertEqual(len(UserProfile.objects.all()), 11)
		self.assertEqual(len(UserFinance.objects.all()), 11)

	def test_unsuccess_post_identification(self):
		response = self.client.post(
			reverse(view_user),
			data = json.dumps(self.object_json_identification_r),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEqual(response.data['message'],'Identification/email already exists')

		self.assertEqual(len(UserProfile.objects.all()), 11)
		self.assertEqual(len(UserFinance.objects.all()), 11)

	def test_unsuccess_post_email(self):
		response = self.client.post(
			reverse(view_user),
			data = json.dumps(self.object_json_email_r),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEqual(response.data['message'],'Identification/email already exists')

		self.assertEqual(len(UserProfile.objects.all()), 11)
		self.assertEqual(len(UserFinance.objects.all()), 11)

	def test_get_users(self):
		response = self.client.get(
			"%s?page=1" % reverse(view_user),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']), 10)
		self.assertEqual(response.data['num_pages'], 2)
		for user in response.data['list']:
			self.assertIsNotNone(user['id'])
			self.assertIsNotNone(user['identification'])
			self.assertIsNotNone(user['full_name'])
			self.assertIsNotNone(user['email'])
			self.assertIsNotNone(user['role'])

	def test_get_users_all(self):
		response = self.client.get(
			reverse(view_user),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']), 11)
		for user in response.data['list']:
			self.assertIsNotNone(user['id'])
			self.assertIsNotNone(user['identification'])
			self.assertIsNotNone(user['full_name'])
			self.assertIsNotNone(user['email'])
			self.assertIsNotNone(user['role'])

	def test_get_users_empty(self):
		response = self.client.get(
			"%s?page=3" % reverse(view_user),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),0)
		self.assertEqual(response.data['num_pages'],2)

	def test_get_users_error_pagination(self):
		response = self.client.get(
			"%s?page=0" % reverse(view_user),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response.data['message'],'Page number must be greater than 0')

	def test_get_user(self):
		response = self.client.get(
			reverse(view_user_detail,kwargs={'id': 1}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['user']['id'],1)
		self.assertEqual(response.data['user']['identification'],99999)
		self.assertEqual(response.data['user']['first_name'],'Foo Name')
		self.assertEqual(response.data['user']['last_name'],'Foo Last Name')
		self.assertEqual(response.data['user']['email'],'mail_for_tests@mail.com')
		self.assertEqual(response.data['user']['role'],0)
		self.assertEqual(response.data['user']['role_display'], 'ADMIN')
		self.assertEqual(response.data['finance']['contributions'],2000)
		self.assertEqual(response.data['finance']['balance_contributions'],2000)
		self.assertEqual(response.data['finance']['total_quota'],1000)
		self.assertEqual(response.data['finance']['available_quota'],500)
		self.assertEqual(response.data['finance']['utilized_quota'],0)

	def test_get_session_user(self):
		response = self.client.get(
			reverse(view_user_detail,kwargs={'id': -1}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['user']['id'],1)
		self.assertEqual(response.data['user']['identification'],99999)
		self.assertEqual(response.data['user']['first_name'],'Foo Name')
		self.assertEqual(response.data['user']['last_name'],'Foo Last Name')
		self.assertEqual(response.data['user']['email'],'mail_for_tests@mail.com')
		self.assertEqual(response.data['user']['role'],0)
		self.assertEqual(response.data['user']['role_display'], 'ADMIN')
		self.assertEqual(response.data['finance']['contributions'],2000)
		self.assertEqual(response.data['finance']['balance_contributions'],2000)
		self.assertEqual(response.data['finance']['total_quota'],1000)
		self.assertEqual(response.data['finance']['available_quota'],500)
		self.assertEqual(response.data['finance']['utilized_quota'],0)

	def test_get_user_not_found(self):
		response = self.client.get(
			reverse(view_user_detail,kwargs={'id': 2}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_delete_user(self):
		response = self.client.delete(
			reverse(view_user_detail,kwargs={'id': 2}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

		response = self.client.delete(
			reverse(view_user_detail,kwargs={'id': 1}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		user = User.objects.get(id = 1)
		self.assertFalse(user.is_active)

		response = self.client.get(
			reverse(view_user_detail,kwargs={'id': 1}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
		try:
			self.get_token('mail_for_tests@mail.com','password')
			self.fail('That account is inactive')
		except KeyError:
			pass

	def test_patch_user(self):
		self.object_json_user_update['type'] = 'personal'
		response = self.client.patch(
			reverse(view_user_detail,kwargs={'id': 2}),
			data=json.dumps(self.object_json_user_update),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

		response = self.client.patch(
			reverse(view_user_detail,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		user = UserProfile.objects.get(id=1)
		self.assertEqual(user.first_name,'Foo Name update')
		self.assertEqual(user.last_name,'Last Name update')
		self.assertEqual(user.email,'mail_updated@mail.com2')
		self.assertEqual(user.username,'mail_updated@mail.com2')

	def test_patch_user_finance(self):
		self.object_json_user_update['type'] = 'finance'
		response = self.client.patch(
			reverse(view_user_detail,kwargs={'id': 2}),
			data=json.dumps(self.object_json_user_update),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

		response = self.client.patch(
			reverse(view_user_detail,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		user_finance = UserFinance.objects.get(user_id=1)
		self.assertEqual(user_finance.contributions, 2000)
		self.assertEqual(user_finance.balance_contributions, 2000)
		self.assertEqual(user_finance.total_quota, 1000)
		self.assertEqual(user_finance.utilized_quota, 500)
		self.assertEqual(user_finance.available_quota, 500)

	def test_patch_user_not_finance(self):
		self.object_json_user_update_same_finance['type'] = 'personal'
		response = self.client.patch(
			reverse(view_user_detail,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update_same_finance),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		user = UserProfile.objects.get(id=1)
		self.assertEqual(user.first_name,'Foo Name update')
		self.assertEqual(user.last_name,'Last Name update')
		self.assertEqual(user.email,'mail_updated@mail.com2')
		self.assertEqual(user.username,'mail_updated@mail.com2')

		self.object_json_user_update_same_finance['type'] = 'finance'
		response = self.client.patch(
			reverse(view_user_detail,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update_same_finance),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		user_finance = UserFinance.objects.get(user_id=1)
		self.assertEqual(user_finance.contributions, 2000)
		self.assertEqual(user_finance.balance_contributions, 2000)
		self.assertEqual(user_finance.total_quota, 1000)
		self.assertEqual(user_finance.utilized_quota, 0)
		self.assertEqual(user_finance.available_quota, 500)

	@patch.object(MailService, 'send_mail')
	def test_patch_user_conflict(self, mock):
		response = self.client.post(
			reverse(view_user),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_201_CREATED)
		self.assertTrue(mock.called)
		mock.assert_called_once()

		self.object_json_user_update_identification_r['type'] = 'personal'
		response = self.client.patch(
			reverse(view_user_detail,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update_identification_r),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


		self.object_json_user_update_email_r['type'] = 'personal'
		response = self.client.patch(
			reverse(view_user_detail,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update_email_r),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

	def test_patch_preferences_not_found(self):
		response = self.client.patch(
			reverse(view_user_detail,kwargs={'id': 111}),
			data='{"type": "preferences", "preferences":{"notifications": true}}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_patch_preferences_notifications(self):
		response = self.client.patch(
			reverse(view_user_detail,kwargs={'id': 1}),
			data='''{"type": "preferences", "preferences":{"notifications": true, "primary_color": "#fff", 
					"secondary_color": "#000"}}''',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		user_preference = UserPreference.objects.get(user_id=1)
		self.assertTrue(user_preference.notifications, True)

		response = self.client.patch(
			reverse(view_user_detail,kwargs={'id': 1}),
			data='''{"type": "preferences", "preferences":{"notifications": false, "primary_color": "#fff", 
					"secondary_color": "#000"}}''',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		user_preference = UserPreference.objects.get(user_id=1)
		self.assertFalse(user_preference.notifications, False)

	@patch.object(MailService, 'send_mail')
	def test_activation_successful(self, mock):
		response = self.client.post(
			reverse(view_user),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_201_CREATED)
		self.assertTrue(mock.called)
		mock.assert_called_once()

		user = UserProfile.objects.get(identification = 123)
		obj = {
			'password':'newPassword123',
			'identification':123,
			'key':user.key_activation
		}

		response = self.client.post(
			reverse(view_user_activate,kwargs={'id': user.id}),
			data = json.dumps(obj),
			content_type='application/json',
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)

		user = UserProfile.objects.get(identification = 123)
		self.assertEqual(user.is_active,True)
		self.assertTrue('pbkdf2_sha256' in user.password)
		self.assertIsNone(user.key_activation)

	@patch.object(MailService, 'send_mail')
	def test_activation_unsuccessful_1(self, mock):
		response = self.client.post(
			reverse(view_user),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_201_CREATED)
		self.assertTrue(mock.called)
		mock.assert_called_once()

		user = UserProfile.objects.get(identification = 123)
		obj = {
			'password':'newPassword123',
			'identification':1234,
			'key':user.key_activation
		}

		response = self.client.post(
			reverse(view_user_activate,kwargs={'id': user.id}),
			data = json.dumps(obj),
			content_type='application/json',
		)
		self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

		user = UserProfile.objects.get(identification = 123)
		self.assertEqual(user.is_active,False)
		self.assertFalse('pbkdf2_sha256' in user.password)
		self.assertIsNotNone(user.key_activation)

	@patch.object(MailService, 'send_mail')
	def test_activation_unsuccessful_2(self, mock):
		response = self.client.post(
			reverse(view_user),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_201_CREATED)
		self.assertTrue(mock.called)
		mock.assert_called_once()

		user = UserProfile.objects.get(identification = 123)
		obj = {
			'password':'newPassword123',
			'identification':1234,
			'key': ''
		}

		response = self.client.post(
			reverse(view_user_activate,kwargs={'id': user.id}),
			data = json.dumps(obj),
			content_type='application/json',
		)
		self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

		user = UserProfile.objects.get(identification = 123)
		self.assertEqual(user.is_active,False)
		self.assertFalse('pbkdf2_sha256' in user.password)
		self.assertIsNotNone(user.key_activation)

	@patch.object(MailService, 'send_mail')
	def test_activation_unsuccessful_3(self, mock):
		response = self.client.post(
			reverse(view_user),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_201_CREATED)
		self.assertTrue(mock.called)
		mock.assert_called_once()

		user = UserProfile.objects.get(identification = 123)
		obj = {
			'password':'newPassword123',
			'identification':1234
		}

		response = self.client.post(
			reverse(view_user_activate, kwargs={'id': user.id}),
			data = json.dumps(obj),
			content_type='application/json',
		)
		self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

		user = UserProfile.objects.get(identification = 123)
		self.assertEqual(user.is_active,False)
		self.assertFalse('pbkdf2_sha256' in user.password)
		self.assertIsNotNone(user.key_activation)

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
			reverse(view_user),
			data=encode_multipart('file',file),
			content_type='multipart/form-data; boundary=file',
			**self.get_auth_header(self.token)
		)

		self.assertEqual(response.status_code,status.HTTP_200_OK)

		user_finance = UserFinance.objects.get(user_id=5)
		self.assertEqual(user_finance.balance_contributions,100)
		self.assertEqual(user_finance.total_quota,1000)
		self.assertEqual(user_finance.contributions,200)
		self.assertEqual(user_finance.utilized_quota,300)
		self.assertEqual(user_finance.available_quota,700)

		user_finance = UserFinance.objects.get(user_id=6)
		self.assertEqual(user_finance.balance_contributions,400)
		self.assertEqual(user_finance.total_quota,1000)
		self.assertEqual(user_finance.contributions,500)
		self.assertEqual(user_finance.utilized_quota,600)
		self.assertEqual(user_finance.available_quota,400)

		user_finance = UserFinance.objects.get(user_id=7)
		self.assertEqual(user_finance.balance_contributions,700)
		self.assertEqual(user_finance.total_quota,1000)
		self.assertEqual(user_finance.contributions,800)
		self.assertEqual(user_finance.utilized_quota,900)
		self.assertEqual(user_finance.available_quota,100)

	def test_user_apps_not_found(self):
		response = self.client.post(
			reverse(view_user_apps, kwargs={'app': 'noexist'}),
			**self.get_auth_header(self.token)
		)

		self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

	def test_get_users_birthdate(self):
		response = self.client.post(
			reverse(view_user_apps, kwargs={'app': 'birthdates'}),
			**self.get_auth_header(self.token)
		)

		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data), 11)
		for i in range(len(response.data)):
			self.assertEqual(response.data[i]['birthdate'], None)

	def test_get_powers_exception(self):
		response = self.client.post(
			reverse(view_user_apps, kwargs={'app': 'power'}),
			**self.get_auth_header(self.token),
			data = json.dumps({
				'type': 'get',
				'page': 2
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code,status.HTTP_500_INTERNAL_SERVER_ERROR)

	def test_get_powers_empty(self):
		response = self.client.post(
			reverse(view_user_apps, kwargs={'app': 'power'}),
			**self.get_auth_header(self.token),
			data = json.dumps({
				'type': 'get',
				'page': 2,
				'obj': 'requestee'
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']), 0)
		self.assertEqual(response.data['num_pages'], 1)

	def test_post_power(self):
		self.assertEqual(len(Power.objects.all()), 0)
		user = UserProfile.objects.get(identification=1001)

		response = self.client.post(
			reverse(view_user_apps, kwargs={'app': 'power'}),
			**self.get_auth_header(self.token),
			data = json.dumps({
				'type': 'post',
				'meeting_date': '2020-01-01',
				'requestee': user.id
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(response.data, None)
		self.assertEqual(len(Power.objects.all()), 1)

	def test_get_powers_pagination(self):
		self.assertEqual(len(Power.objects.all()), 0)
		user = UserProfile.objects.get(identification=1001)

		for i in range(11):
			response = self.client.post(
				reverse(view_user_apps, kwargs={'app': 'power'}),
				**self.get_auth_header(self.token),
				data = json.dumps({
					'type': 'post',
					'meeting_date': '2020-01-01',
					'requestee': user.id
				}),
				content_type='application/json',
			)
			self.assertEqual(response.status_code,status.HTTP_200_OK)
		
		response = self.client.post(
			reverse(view_user_apps, kwargs={'app': 'power'}),
			**self.get_auth_header(self.token),
			data = json.dumps({
				'type': 'get',
				'page': 1,
				'obj': 'requested'
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']), 10)
		self.assertEqual(response.data['num_pages'], 2)

	def test_patch_power_denied(self):
		user = UserProfile.objects.get(identification=1001)
		response = self.client.post(
			reverse(view_user_apps, kwargs={'app': 'power'}),
			**self.get_auth_header(self.token),
			data = json.dumps({
				'type': 'post',
				'meeting_date': '2020-01-01',
				'requestee': user.id
			}),
			content_type='application/json',
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)

		power = Power.objects.all()[0]
		response = self.client.post(
			reverse(view_user_apps, kwargs={'app': 'power'}),
			**self.get_auth_header(self.token),
			data = json.dumps({
				'type': 'patch',
				'id': power.id,
				'state': 2
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(response.data, None)
		power = Power.objects.all()[0]
		self.assertEqual(power.state, 2)

	@patch.object(MailService, 'send_mail')
	def test_patch_power_approved(self, mock):
		user = UserProfile.objects.get(identification=1001)
		response = self.client.post(
			reverse(view_user_apps, kwargs={'app': 'power'}),
			**self.get_auth_header(self.token),
			data = json.dumps({
				'type': 'post',
				'meeting_date': '2020-01-01',
				'requestee': user.id
			}),
			content_type='application/json',
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)

		power = Power.objects.all()[0]
		response = self.client.post(
			reverse(view_user_apps, kwargs={'app': 'power'}),
			**self.get_auth_header(self.token),
			data = json.dumps({
				'type': 'patch',
				'id': power.id,
				'state': 1
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(response.data, None)
		power = Power.objects.all()[0]
		self.assertEqual(power.state, 1)
		self.assertTrue(mock.called)
		mock.assert_called_once()