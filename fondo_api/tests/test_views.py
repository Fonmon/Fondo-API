import json
from decimal import Decimal
from rest_framework import status
from django.test import TestCase, Client
from django.test.client import encode_multipart
from django.urls import reverse
from ..models import *
from django.contrib.auth.models import User
from django.core import mail
from mock import patch

# initialize the APIClient app
client = Client()
THREEPLACES = Decimal(10) ** -3

# Paths API tests
view_get_update_loan = 'view_get_update_loan'
view_get_post_loans = 'view_get_post_loans'
view_get_post_users = 'view_get_post_users'
view_get_update_delete_user = 'view_get_update_delete_user'
view_activate_user = 'view_activate_user'
view_logout = 'view_logout'

def create_user():
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

def get_token(username, password):
	body = {
		'username':'{}'.format(username),
		'password':'{}'.format(password)
	}
	response = client.post(
		reverse('obtain_auth_token'),
		data = json.dumps(body),
		content_type='application/json',
	)
	return response.data['token']

def get_auth_header(token):
	return {'HTTP_AUTHORIZATION': "Token {}".format(token)}

class UserViewTest(TestCase):

	def setUp(self):
		create_user()
		self.token = get_token('mail_for_tests@mail.com','password')
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
		response = client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**get_auth_header(self.token)
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
		response = client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEquals(response.data['message'],'Invalid email')

		self.assertEquals(len(UserProfile.objects.all()),1)
		self.assertEquals(len(UserFinance.objects.all()),1)

	def test_unsuccess_post_identification(self):
		response = client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json_identification_r),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEquals(response.data['message'],'Identification/email already exists')

		self.assertEquals(len(UserProfile.objects.all()),1)
		self.assertEquals(len(UserFinance.objects.all()),1)

	def test_unsuccess_post_email(self):
		response = client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json_email_r),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEquals(response.data['message'],'Identification/email already exists')

		self.assertEquals(len(UserProfile.objects.all()),1)
		self.assertEquals(len(UserFinance.objects.all()),1)

	def test_get_users(self):
		response = client.get(
			reverse(view_get_post_users),
			**get_auth_header(self.token)
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
		response = client.get(
			"%s?page=2" % reverse(view_get_post_users),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),0)
		self.assertEquals(response.data['num_pages'],1)

	def test_get_users_error_pagination(self):
		response = client.get(
			"%s?page=0" % reverse(view_get_post_users),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEquals(response.data['message'],'Page number must be greater or equal than 0')

	def test_get_user(self):
		response = client.get(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			**get_auth_header(self.token)
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
		response = client.get(
			reverse(view_get_update_delete_user,kwargs={'id': -1}),
			**get_auth_header(self.token)
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
		response = client.get(
			reverse(view_get_update_delete_user,kwargs={'id': 2}),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_delete_user(self):
		response = client.delete(
			reverse(view_get_update_delete_user,kwargs={'id': 2}),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

		response = client.delete(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		user = User.objects.get(id = 1)
		self.assertFalse(user.is_active)

		response = client.get(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_401_UNAUTHORIZED)
		try:
			get_token('mail_for_tests@mail.com','password')
			self.fail('That account is inactive')
		except KeyError:
			pass

	def test_patch_user(self):
		response = client.patch(
			reverse(view_get_update_delete_user,kwargs={'id': 2}),
			data=json.dumps(self.object_json_user_update),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

		response = client.patch(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)

		user = UserProfile.objects.get(id=1)
		self.assertEquals(user.first_name,'Foo Name update')
		self.assertEquals(user.last_name,'Last Name update')
		self.assertEquals(user.email,'mail_updated@mail.com2')
		self.assertEquals(user.username,'mail_updated@mail.com2')

	def test_patch_user_not_finance(self):
		response = client.patch(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update_same_finance),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)

		user = UserProfile.objects.get(id=1)
		self.assertEquals(user.first_name,'Foo Name update')
		self.assertEquals(user.last_name,'Last Name update')
		self.assertEquals(user.email,'mail_updated@mail.com2')
		self.assertEquals(user.username,'mail_updated@mail.com2')

	def test_patch_user_conflict(self):
		response = client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_201_CREATED)
		self.assertEquals(len(mail.outbox),1)
		self.assertEquals(mail.outbox[0].subject,'[Fondo Montañez] Activación de cuenta')
		self.assertEquals(len(mail.outbox[0].to),1)
		self.assertEquals(mail.outbox[0].to[0],'mail@mail.com')

		response = client.patch(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update_identification_r),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_409_CONFLICT)

		response = client.patch(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			data=json.dumps(self.object_json_user_update_email_r),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_409_CONFLICT)

	def test_activation_successful(self):
		response = client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**get_auth_header(self.token)
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

		response = client.post(
			reverse(view_activate_user,kwargs={'id': user.id}),
			data = json.dumps(obj),
			content_type='application/json',
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)

		user = UserProfile.objects.get(identification = 123)
		self.assertEquals(user.is_active,True)
		self.assertTrue('pbkdf2_sha256' in user.password)

	def test_activation_unsuccessful(self):
		response = client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**get_auth_header(self.token)
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

		response = client.post(
			reverse(view_activate_user,kwargs={'id': user.id}),
			data = json.dumps(obj),
			content_type='application/json',
		)
		self.assertEquals(response.status_code,status.HTTP_404_NOT_FOUND)

		user = UserProfile.objects.get(identification = 123)
		self.assertEquals(user.is_active,False)
		self.assertFalse('pbkdf2_sha256' in user.password)

	def test_logout(self):
		response = client.post(
			reverse(view_logout),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		response = client.post(
			reverse(view_logout),
			**get_auth_header(self.token)
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
		response = client.patch(
			reverse(view_get_post_users),
			data=encode_multipart('file',file),
			content_type='multipart/form-data; boundary=file',
			**get_auth_header(self.token)
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

class LoanViewTest(TestCase):

	def setUp(self):
		create_user()
		self.token = get_token('mail_for_tests@mail.com','password')
		self.loan_with_quota_fee_5 = {
			'value':100,
			'timelimit': 5,
			'disbursement_date': '2017-12-9',
			'comments':'',
			'payment':0,
			'fee': 0
		}
		self.loan_with_quota_fee_10 = {
			'value':200,
			'timelimit': 10,
			'disbursement_date': '2017-11-9',
			'comments':'',
			'payment':1,
			'fee': 0
		}
		self.loan_with_quota_fee_20 = {
			'value':300,
			'timelimit': 20,
			'disbursement_date': '2018-1-1',
			'comments':'',
			'payment':0,
			'fee': 0
		}
		self.loan_with_not_quota = {
			'value':600,
			'timelimit': 8,
			'disbursement_date': '2017-12-9',
			'comments':'',
			'payment':0,
			'fee': 0
		}

	def test_post_loan_1(self):
		response = client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_5),
			content_type='application/json',
			**get_auth_header(self.token)
		)

		self.assertEquals(response.status_code, status.HTTP_201_CREATED)
		loan = Loan.objects.get(user_id = 1)
		self.assertEquals(response.data['id'],loan.id)
		self.assertEquals(loan.value,100)
		self.assertEquals(loan.get_fee_display(),'MONTHLY')
		self.assertEquals(loan.get_state_display(),'WAITING_APPROVAL')
		self.assertEquals(loan.rate,Decimal(0.02).quantize(THREEPLACES))
		self.assertEquals(loan.disbursement_date.year, 2017)
		self.assertEquals(loan.disbursement_date.month, 12)
		self.assertEquals(loan.disbursement_date.day, 9)
		self.assertEquals(loan.comments,'')
		self.assertEquals(loan.payment,0)
		self.assertEquals(loan.get_payment_display(),'CASH')

	def test_post_loan_2(self):
		response = client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(self.token)
		)

		self.assertEquals(response.status_code, status.HTTP_201_CREATED)
		loan = Loan.objects.get(user_id = 1)
		self.assertEquals(response.data['id'],loan.id)
		self.assertEquals(loan.value,200)
		self.assertEquals(loan.get_fee_display(),'MONTHLY')
		self.assertEquals(loan.get_state_display(),'WAITING_APPROVAL')
		self.assertEquals(loan.rate,Decimal(0.025).quantize(THREEPLACES))
		self.assertEquals(loan.disbursement_date.year, 2017)
		self.assertEquals(loan.disbursement_date.month, 11)
		self.assertEquals(loan.disbursement_date.day, 9)
		self.assertEquals(loan.comments,'')
		self.assertEquals(loan.payment,1)
		self.assertEquals(loan.get_payment_display(),'BANK_ACCOUNT')

	def test_post_loan_3(self):
		response = client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_20),
			content_type='application/json',
			**get_auth_header(self.token)
		)

		self.assertEquals(response.status_code, status.HTTP_201_CREATED)
		loan = Loan.objects.get(user_id = 1)
		self.assertEquals(response.data['id'],loan.id)
		self.assertEquals(loan.value,300)
		self.assertEquals(loan.get_fee_display(),'MONTHLY')
		self.assertEquals(loan.get_state_display(),'WAITING_APPROVAL')
		self.assertEquals(loan.rate,Decimal(0.03).quantize(THREEPLACES))
		self.assertEquals(loan.disbursement_date.year, 2018)
		self.assertEquals(loan.disbursement_date.month, 1)
		self.assertEquals(loan.disbursement_date.day, 1)
		self.assertEquals(loan.comments,'')
		self.assertEquals(loan.payment,0)
		self.assertEquals(loan.get_payment_display(),'CASH')

	def test_post_loan_error(self):
		response = client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_not_quota),
			content_type='application/json',
			**get_auth_header(self.token)
		)

		self.assertEquals(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
		self.assertEquals(response.data['message'],'User does not have available quota')
		self.assertEquals(len(Loan.objects.filter(user_id = 1)),0)

	def test_get_loans_paginator(self):
		for i in range(25):
			client.post(
				reverse(view_get_post_loans),
				data = json.dumps(self.loan_with_quota_fee_5),
				content_type='application/json',
				**get_auth_header(self.token)
			)
		self.assertEquals(len(Loan.objects.all()),25)
		response = client.get(
			reverse(view_get_post_loans),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),10)
		self.assertEquals(response.data['num_pages'],3)
		response = client.get(
			"%s?page=0" % reverse(view_get_post_loans),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_400_BAD_REQUEST)
		self.assertEquals(response.data['message'],'Page number must be greater or equal than 0')
		response = client.get(
			"%s?page=3" % reverse(view_get_post_loans),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),5)
		self.assertEquals(response.data['num_pages'],3)

		response = client.get(
			"%s?page=4" % reverse(view_get_post_loans),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),0)
		self.assertEquals(response.data['num_pages'],3)

	def test_get_loans(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_5),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		user = UserProfile.objects.create_user(
			id = 2,
			first_name = 'Foo Name',
			last_name = 'Foo Last Name',
			identification = 99899,
			email = "mail_for_tests_2@mail.com",
			username = "mail_for_tests_2@mail.com",
			password = "password",
			role = 3
		)
		UserFinance.objects.create(
			contributions= 2000,
			balance_contributions= 2000,
			total_quota= 1000,
			available_quota= 500,
			user= user
		)
		token = get_token('mail_for_tests_2@mail.com','password')
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_20),
			content_type='application/json',
			**get_auth_header(token)
		)

		response = client.get(
			reverse(view_get_post_loans),
			**get_auth_header(token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),1)
		for loan in response.data['list']:
			self.assertIsNotNone(loan['user_full_name'])
			self.assertIsNotNone(loan['state'])
			self.assertIsNotNone(loan['value'])
			self.assertIsNotNone(loan['timelimit'])
			self.assertIsNotNone(loan['disbursement_date'])
			self.assertIsNotNone(loan['fee'])
			self.assertIsNotNone(loan['rate'])
			self.assertIsNotNone(loan['id'])
			self.assertIsNotNone(loan['created_at'])

		response = client.get(
			reverse(view_get_post_loans),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),2)
		for loan in response.data['list']:
			self.assertIsNotNone(loan['user_full_name'])
			self.assertIsNotNone(loan['state'])
			self.assertIsNotNone(loan['value'])
			self.assertIsNotNone(loan['timelimit'])
			self.assertIsNotNone(loan['disbursement_date'])
			self.assertIsNotNone(loan['fee'])
			self.assertIsNotNone(loan['rate'])
			self.assertIsNotNone(loan['id'])
			self.assertIsNotNone(loan['created_at'])

		response = client.get(
			"%s?all_loans=true" % reverse(view_get_post_loans),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),3)

		response = client.get(
			"%s?all_loans=true" % reverse(view_get_post_loans),
			**get_auth_header(token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),1)

	def test_get_loans_filter(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_5),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		response = client.get(
			"%s?state=5" % reverse(view_get_post_loans),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_400_BAD_REQUEST)
		self.assertEquals(response.data['message'],'State must be between 0 and 4')

		response = client.get(
			"%s?state=1" % reverse(view_get_post_loans),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),0)

		response = client.get(
			"%s?state=0" % reverse(view_get_post_loans),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),2)
		for loan in response.data['list']:
			self.assertEquals(loan['state'],0)

	def test_get_loans_filter_all(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_5),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(self.token)
		)

		response = client.get(
			"%s?state=0&all_loans=true" % reverse(view_get_post_loans),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data['list']),2)
		for loan in response.data['list']:
			self.assertEquals(loan['state'],0)

	def test_update_loan_approved_monthly(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":1}',
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(response.data['total_payment'],228)
		self.assertEquals(response.data['minimum_payment'],25)
		self.assertEquals(response.data['payday_limit'],'2017-12-09')
		self.assertEquals(len(mail.outbox),1)
		self.assertEquals(mail.outbox[0].subject,'[Fondo Montañez] Solicitud de crédito')
		self.assertEquals(len(mail.outbox[0].to),1)
		self.assertEquals(mail.outbox[0].to[0],'mail_for_tests@mail.com')
		content, mimetype = mail.outbox[0].alternatives[0]
		self.assertEquals(mimetype,'text/html')
		subcontent = 'crédito número: {},'.format(loan.id)
		self.assertTrue(subcontent in content)
		subcontent = '<strong>APROBADA</strong>'
		self.assertTrue(subcontent in content)
		subcontent = '<table style="width:100%" border="1"><tr><th>Cuota</th><th>Saldo inicial</th><th>Fecha inicial</th><th>Intereses</th><th>Abono a capital</th><th>Fecha de pago</th><th>Valor pago</th><th>Saldo final</th></tr><tr><td>1</td><td>$200</td><td>2017-11-09</td><td>$5</td><td>$20</td><td>2017-12-09</td><td>$25</td><td>$180</td></tr><tr><td>2</td><td>$180</td><td>2017-12-09</td><td>$4</td><td>$20</td><td>2018-01-09</td><td>$24</td><td>$160</td></tr><tr><td>3</td><td>$160</td><td>2018-01-09</td><td>$4</td><td>$20</td><td>2018-02-09</td><td>$24</td><td>$140</td></tr><tr><td>4</td><td>$140</td><td>2018-02-09</td><td>$3</td><td>$20</td><td>2018-03-09</td><td>$23</td><td>$120</td></tr><tr><td>5</td><td>$120</td><td>2018-03-09</td><td>$3</td><td>$20</td><td>2018-04-09</td><td>$23</td><td>$100</td></tr><tr><td>6</td><td>$100</td><td>2018-04-09</td><td>$2</td><td>$20</td><td>2018-05-09</td><td>$22</td><td>$80</td></tr><tr><td>7</td><td>$80</td><td>2018-05-09</td><td>$2</td><td>$20</td><td>2018-06-09</td><td>$22</td><td>$60</td></tr><tr><td>8</td><td>$60</td><td>2018-06-09</td><td>$1</td><td>$20</td><td>2018-07-09</td><td>$21</td><td>$40</td></tr><tr><td>9</td><td>$40</td><td>2018-07-09</td><td>$1</td><td>$20</td><td>2018-08-09</td><td>$21</td><td>$20</td></tr><tr><td>10</td><td>$20</td><td>2018-08-09</td><td>$0</td><td>$20</td><td>2018-09-09</td><td>$20</td><td>$0</td></tr></table>'
		self.assertTrue(subcontent in content)

		loan = Loan.objects.get(user_id = 1)
		self.assertEquals(loan.state,1)
		self.assertEquals(loan.get_state_display(),'APPROVED')

		response = client.get(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		self.assertEquals(response.data['loan']['id'],loan.id)
		self.assertEquals(response.data['loan']['value'],200)
		self.assertEquals(response.data['loan']['timelimit'],10)
		self.assertEquals(response.data['loan']['disbursement_date'],'2017-11-09')
		self.assertEquals(response.data['loan']['payment'],1)
		self.assertEquals(response.data['loan']['fee'],0)
		self.assertEquals(response.data['loan']['comments'],'')
		self.assertEquals(response.data['loan']['state'],1)
		self.assertEquals(response.data['loan']['user_full_name'],'Foo Name Foo Last Name')
		self.assertEquals(Decimal(response.data['loan']['rate']).quantize(THREEPLACES),Decimal(0.025).quantize(THREEPLACES))
		self.assertIsNotNone(response.data['loan']['created_at'])

		self.assertEquals(response.data['loan_detail']['total_payment'],228)
		self.assertEquals(response.data['loan_detail']['minimum_payment'],25)
		self.assertEquals(response.data['loan_detail']['payday_limit'],'2017-12-09')

	def test_update_loan_approved_unique(self):
		self.loan_with_quota_fee_10['fee']=1
		self.loan_with_quota_fee_10['timelimit']=13
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":1}',
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(response.data['total_payment'],278)
		self.assertEquals(response.data['minimum_payment'],278)
		self.assertEquals(response.data['payday_limit'],'2018-12-09')
		self.assertEquals(len(mail.outbox),1)
		self.assertEquals(mail.outbox[0].subject,'[Fondo Montañez] Solicitud de crédito')
		self.assertEquals(len(mail.outbox[0].to),1)
		self.assertEquals(mail.outbox[0].to[0],'mail_for_tests@mail.com')
		content, mimetype = mail.outbox[0].alternatives[0]
		self.assertEquals(mimetype,'text/html')
		subcontent = 'crédito número: {},'.format(loan.id)
		self.assertTrue(subcontent in content)
		subcontent = '<strong>APROBADA</strong>'
		self.assertTrue(subcontent in content)
		subcontent = '<table style="width:100%" border="1"><tr><th>Cuota</th><th>Saldo inicial</th><th>Fecha inicial</th><th>Intereses</th><th>Abono a capital</th><th>Fecha de pago</th><th>Valor pago</th><th>Saldo final</th></tr><tr><td>1</td><td>$200</td><td>2017-11-09</td><td>$78</td><td>$200</td><td>2018-12-09</td><td>$278</td><td>$0</td></tr></table>'
		self.assertTrue(subcontent in content)

		loan = Loan.objects.get(user_id = 1)
		self.assertEquals(loan.state,1)
		self.assertEquals(loan.get_state_display(),'APPROVED')

		response = client.get(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		self.assertEquals(response.data['loan']['id'],loan.id)
		self.assertEquals(response.data['loan']['value'],200)
		self.assertEquals(response.data['loan']['timelimit'],13)
		self.assertEquals(response.data['loan']['disbursement_date'],'2017-11-09')
		self.assertEquals(response.data['loan']['payment'],1)
		self.assertEquals(response.data['loan']['fee'],1)
		self.assertEquals(response.data['loan']['comments'],'')
		self.assertEquals(response.data['loan']['state'],1)
		self.assertEquals(response.data['loan']['user_full_name'],'Foo Name Foo Last Name')
		self.assertEquals(Decimal(response.data['loan']['rate']).quantize(THREEPLACES),Decimal(0.03).quantize(THREEPLACES))
		self.assertIsNotNone(response.data['loan']['created_at'])

		self.assertEquals(response.data['loan_detail']['total_payment'],278)
		self.assertEquals(response.data['loan_detail']['minimum_payment'],278)
		self.assertEquals(response.data['loan_detail']['payday_limit'],'2018-12-09')

	def test_update_loan_approved_repeat_email(self):
		self.loan_with_quota_fee_10['fee']=1
		self.loan_with_quota_fee_10['timelimit']=13
		user = UserProfile.objects.create_user(
			id = 2,
			first_name = 'Foo Name',
			last_name = 'Foo Last Name',
			identification = 99899,
			email = "mail_for_tests_2@mail.com",
			username = "mail_for_tests_2@mail.com",
			password = "password",
			role = 3
		)
		UserFinance.objects.create(
			contributions= 2000,
			balance_contributions= 2000,
			total_quota= 1000,
			available_quota= 500,
			user= user
		)
		token = get_token('mail_for_tests_2@mail.com','password')

		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(token)
		)

		loan = Loan.objects.get(user_id = 2)
		response = client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":1}',
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(response.data['total_payment'],278)
		self.assertEquals(response.data['minimum_payment'],278)
		self.assertEquals(response.data['payday_limit'],'2018-12-09')
		self.assertEquals(len(mail.outbox),1)
		self.assertEquals(mail.outbox[0].subject,'[Fondo Montañez] Solicitud de crédito')
		self.assertEquals(len(mail.outbox[0].to),2)
		self.assertEquals(mail.outbox[0].to[0],'mail_for_tests@mail.com')
		self.assertEquals(mail.outbox[0].to[1],'mail_for_tests_2@mail.com')
		content, mimetype = mail.outbox[0].alternatives[0]
		self.assertEquals(mimetype,'text/html')
		subcontent = 'crédito número: {},'.format(loan.id)
		self.assertTrue(subcontent in content)
		subcontent = '<strong>APROBADA</strong>'
		self.assertTrue(subcontent in content)
		subcontent = '<table style="width:100%" border="1"><tr><th>Cuota</th><th>Saldo inicial</th><th>Fecha inicial</th><th>Intereses</th><th>Abono a capital</th><th>Fecha de pago</th><th>Valor pago</th><th>Saldo final</th></tr><tr><td>1</td><td>$200</td><td>2017-11-09</td><td>$78</td><td>$200</td><td>2018-12-09</td><td>$278</td><td>$0</td></tr></table>'
		self.assertTrue(subcontent in content)

		loan = Loan.objects.get(user_id = 2)
		self.assertEquals(loan.state,1)
		self.assertEquals(loan.get_state_display(),'APPROVED')

	def test_update_loan_state(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":3}',
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)

		loan = Loan.objects.get(user_id = 1)
		self.assertEquals(loan.state,3)
		self.assertEquals(loan.get_state_display(),'PAID_OUT')

	def test_update_loan_denied(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":2}',
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(mail.outbox),1)
		self.assertEquals(mail.outbox[0].subject,'[Fondo Montañez] Solicitud de crédito')
		self.assertEquals(len(mail.outbox[0].to),1)
		self.assertEquals(mail.outbox[0].to[0],'mail_for_tests@mail.com')
		content, mimetype = mail.outbox[0].alternatives[0]
		self.assertEquals(mimetype,'text/html')
		subcontent = 'crédito número: {},'.format(loan.id)
		self.assertTrue(subcontent in content)
		subcontent = '<strong>RECHAZADA</strong>'
		self.assertTrue(subcontent in content)

		loan = Loan.objects.get(user_id = 1)
		self.assertEquals(loan.state,2)
		self.assertEquals(loan.get_state_display(),'DENIED')

	def test_update_loan_denied_repeat_email(self):
		user = UserProfile.objects.create_user(
			id = 2,
			first_name = 'Foo Name',
			last_name = 'Foo Last Name',
			identification = 99899,
			email = "mail_for_tests_2@mail.com",
			username = "mail_for_tests_2@mail.com",
			password = "password",
			role = 3
		)
		UserFinance.objects.create(
			contributions= 2000,
			balance_contributions= 2000,
			total_quota= 1000,
			available_quota= 500,
			user= user
		)
		token = get_token('mail_for_tests_2@mail.com','password')

		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(token)
		)

		loan = Loan.objects.get(user_id = 2)
		response = client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":2}',
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(mail.outbox),1)
		self.assertEquals(mail.outbox[0].subject,'[Fondo Montañez] Solicitud de crédito')
		self.assertEquals(len(mail.outbox[0].to),2)
		self.assertEquals(mail.outbox[0].to[0],'mail_for_tests@mail.com')
		self.assertEquals(mail.outbox[0].to[1],'mail_for_tests_2@mail.com')
		content, mimetype = mail.outbox[0].alternatives[0]
		self.assertEquals(mimetype,'text/html')
		subcontent = 'crédito número: {},'.format(loan.id)
		self.assertTrue(subcontent in content)
		subcontent = '<strong>RECHAZADA</strong>'
		self.assertTrue(subcontent in content)

		loan = Loan.objects.get(user_id = 2)
		self.assertEquals(loan.state,2)
		self.assertEquals(loan.get_state_display(),'DENIED')

	def test_update_loan_not_found(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id+1}),
			data = '{"state":2}',
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_404_NOT_FOUND)
		self.assertEquals(response.data['message'],'Loan does not exist')

	def test_update_loan_exceeded(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id+1}),
			data = '{"state":5}',
			content_type='application/json',
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code,status.HTTP_400_BAD_REQUEST)
		self.assertEquals(response.data['message'],'State must be less or equal than 3')

	def test_get_loan(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header(self.token)
		)
		loan = Loan.objects.get(user_id = 1)

		response = client.get(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		self.assertEquals(response.data['loan']['id'],loan.id)
		self.assertEquals(response.data['loan']['value'],200)
		self.assertEquals(response.data['loan']['timelimit'],10)
		self.assertEquals(response.data['loan']['disbursement_date'],'2017-11-09')
		self.assertEquals(response.data['loan']['payment'],1)
		self.assertEquals(response.data['loan']['fee'],0)
		self.assertEquals(response.data['loan']['comments'],'')
		self.assertEquals(response.data['loan']['state'],0)
		self.assertEquals(response.data['loan']['user_full_name'],'Foo Name Foo Last Name')
		self.assertEquals(Decimal(response.data['loan']['rate']).quantize(THREEPLACES),Decimal(0.025).quantize(THREEPLACES))
		self.assertIsNotNone(response.data['loan']['created_at'])

	def test_get_loan_not_found(self):
		response = client.get(
			reverse(view_get_update_loan,kwargs={'id': 2}),
			**get_auth_header(self.token)
		)
		self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

	def create_test_file(self):
		try:
			file = open("testfile.txt","w")
			file.write("1\t1234\t5678\t1/1/2018\r\n")
			file.write("2\t4321\t8765\t2/1/2018\r\n")
			file.write("3\t1\t2\t3/1/2017\r\n")
			file.write("4\t1\t2\t3/1/2017\r\n")
		finally:
			file.close()
		return file

	def test_bulk_update_loans(self):
		user = UserProfile.objects.get(id=1)
		for i in range(3):
			loan = Loan.objects.create(
				id=i+1,
				value=100,
				timelimit= 5,
				disbursement_date= '2000-1-1',
				comments='',
				payment=0,
				fee= 0,
				rate=0,
				user=user
			)
			LoanDetail.objects.create(
				payday_limit="2000-1-1",
				loan=loan
			)
		file = {}
		created_file = self.create_test_file()
		file_reader = open(created_file.name,'r')
		file['file'] = file_reader
		response = client.patch(
			reverse(view_get_post_loans),
			data=encode_multipart('file',file),
			content_type='multipart/form-data; boundary=file',
			**get_auth_header(self.token)
		)

		self.assertEquals(response.status_code,status.HTTP_200_OK)

		loan_detail = LoanDetail.objects.get(loan_id=1)
		self.assertEquals(loan_detail.total_payment,1234)
		self.assertEquals(loan_detail.minimum_payment,5678)
		self.assertEquals(loan_detail.payday_limit.year,2018)
		self.assertEquals(loan_detail.payday_limit.month,1)
		self.assertEquals(loan_detail.payday_limit.day,1)

		loan_detail = LoanDetail.objects.get(loan_id=2)
		self.assertEquals(loan_detail.total_payment,4321)
		self.assertEquals(loan_detail.minimum_payment,8765)
		self.assertEquals(loan_detail.payday_limit.year,2018)
		self.assertEquals(loan_detail.payday_limit.month,1)
		self.assertEquals(loan_detail.payday_limit.day,2)

		loan_detail = LoanDetail.objects.get(loan_id=3)
		self.assertEquals(loan_detail.total_payment,1)
		self.assertEquals(loan_detail.minimum_payment,2)
		self.assertEquals(loan_detail.payday_limit.year,2017)
		self.assertEquals(loan_detail.payday_limit.month,1)
		self.assertEquals(loan_detail.payday_limit.day,3)