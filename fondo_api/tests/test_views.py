import json
from decimal import Decimal
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from ..models import *

# initialize the APIClient app
client = Client()
THREEPLACES = Decimal(10) ** -3

# Paths API tests
view_update_loan = 'view_update_loan'
view_get_post_loans = 'view_get_post_loans'
view_get_post_users = 'view_get_post_users'
view_get_update_delete_user = 'view_get_update_delete_user'

def create_user():
	user = User.objects.create(
		id = 1,
		full_name = 'Foo Full Name',
		identification = 99999
	)
	UserAuth.objects.create(
		email = "mail_for_tests@mail.com",
		password = "pbkdf2_sha256$100000$iGqql2jYhn1b$gik5vcbaSyLZZyFFsU12Pk5TfN8GtR8rXPdCqZPMR3c=",
		is_active = True,
		user = user
	)
	UserFinance.objects.create(
		contributions= 2000,
		balance_contributions= 2000,
		total_quota= 1000,
		available_quota= 500,
		user= user
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
			'role': 2,
			'contributions': 2000,
			'balance_contributions': 2000,
			'total_quota': 1000,
			'available_quota': 500
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
			reverse(view_get_post_users),
			data = json.dumps(self.object_json),
			content_type='application/json',
			**get_auth_header()
		)
		self.assertEquals(response.status_code,status.HTTP_201_CREATED)

		user = User.objects.get(identification = 123)
		self.assertEquals(user.full_name,'Foo Name')
		self.assertEquals(user.identification,123)

		user_auth = UserAuth.objects.get(user_id = user.id)
		self.assertEquals(user_auth.email, "mail@mail.com")
		self.assertEquals(user_auth.role, 2)
		self.assertEquals(user_auth.get_role_display(),'TREASURER')

		user_finance = UserFinance.objects.get(user_id = user.id)
		self.assertEquals(user_finance.contributions, 2000)
		self.assertEquals(user_finance.balance_contributions, 2000)
		self.assertEquals(user_finance.total_quota, 1000)
		self.assertEquals(user_finance.available_quota, 500)

	def test_unsuccess_post_identification(self):
		response = client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json_identification_r),
			content_type='application/json',
			**get_auth_header()
		)
		self.assertEquals(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEquals(response.data['message'],'Identification already exists')

		self.assertEquals(len(User.objects.all()),1)
		self.assertEquals(len(UserAuth.objects.all()),1)
		self.assertEquals(len(UserFinance.objects.all()),1)

	def test_unsuccess_post_email(self):
		response = client.post(
			reverse(view_get_post_users),
			data = json.dumps(self.object_json_email_r),
			content_type='application/json',
			**get_auth_header()
		)
		self.assertEquals(response.status_code,status.HTTP_409_CONFLICT)
		self.assertEquals(response.data['message'],'Email already exists')

		self.assertEquals(len(User.objects.all()),1)
		self.assertEquals(len(UserAuth.objects.all()),1)
		self.assertEquals(len(UserFinance.objects.all()),1)

	def test_get_users(self):
		response = client.get(
			reverse(view_get_post_users),
			**get_auth_header()
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		self.assertEquals(len(response.data),len(User.objects.all()))
		for user in response.data:
			self.assertIsNotNone(user['id'])
			self.assertIsNotNone(user['identification'])
			self.assertIsNotNone(user['full_name'])
			self.assertIsNotNone(user['email'])

	def test_get_user(self):
		response = client.get(
			reverse(view_get_update_delete_user,kwargs={'id': 1}),
			**get_auth_header()
		)
		self.assertEquals(response.status_code, status.HTTP_200_OK)
		self.assertEquals(response.data['id'],1)
		self.assertEquals(response.data['identification'],99999)
		self.assertEquals(response.data['full_name'],'Foo Full Name')
		self.assertEquals(response.data['email'],'mail_for_tests@mail.com')
		self.assertEquals(response.data['role'],'MEMBER')
		self.assertEquals(response.data['contributions'],2000)
		self.assertEquals(response.data['balance_contributions'],2000)
		self.assertEquals(response.data['total_quota'],1000)
		self.assertEquals(response.data['available_quota'],500)

	def test_get_user_not_found(self):
		response = client.get(
			reverse(view_get_update_delete_user,kwargs={'id': 2}),
			**get_auth_header()
		)
		self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)


class LoanViewTest(TestCase):

	def setUp(self):
		create_user()
		self.loan_with_quota_fee_5 = {
			'value':100,
			'timelimit': 5,
			'disbursement_date': '2017-12-9',
			'fee': 0
		}
		self.loan_with_quota_fee_10 = {
			'value':200,
			'timelimit': 10,
			'disbursement_date': '2017-11-9',
			'fee': 0
		}
		self.loan_with_quota_fee_20 = {
			'value':300,
			'timelimit': 20,
			'disbursement_date': '2018-1-1',
			'fee': 0
		}
		self.loan_with_not_quota = {
			'value':600,
			'timelimit': 8,
			'disbursement_date': '2017-12-9',
			'fee': 0
		}

	def test_post_loan_1(self):
		response = client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_5),
			content_type='application/json',
			**get_auth_header()
		)

		self.assertEquals(response.status_code, status.HTTP_201_CREATED)
		loan = Loan.objects.get(user_id = 1)
		self.assertEquals(loan.value,100)
		self.assertEquals(loan.get_fee_display(),'MONTHLY')
		self.assertEquals(loan.get_state_display(),'WAITING_APPROVAL')
		self.assertEquals(loan.rate,Decimal(0.02).quantize(THREEPLACES))
		self.assertEquals(loan.disbursement_date.year, 2017)
		self.assertEquals(loan.disbursement_date.month, 12)
		self.assertEquals(loan.disbursement_date.day, 9)

	def test_post_loan_2(self):
		response = client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header()
		)

		self.assertEquals(response.status_code, status.HTTP_201_CREATED)
		loan = Loan.objects.get(user_id = 1)
		self.assertEquals(loan.value,200)
		self.assertEquals(loan.get_fee_display(),'MONTHLY')
		self.assertEquals(loan.get_state_display(),'WAITING_APPROVAL')
		self.assertEquals(loan.rate,Decimal(0.025).quantize(THREEPLACES))
		self.assertEquals(loan.disbursement_date.year, 2017)
		self.assertEquals(loan.disbursement_date.month, 11)
		self.assertEquals(loan.disbursement_date.day, 9)

	def test_post_loan_3(self):
		response = client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_20),
			content_type='application/json',
			**get_auth_header()
		)

		self.assertEquals(response.status_code, status.HTTP_201_CREATED)
		loan = Loan.objects.get(user_id = 1)
		self.assertEquals(loan.value,300)
		self.assertEquals(loan.get_fee_display(),'MONTHLY')
		self.assertEquals(loan.get_state_display(),'WAITING_APPROVAL')
		self.assertEquals(loan.rate,Decimal(0.03).quantize(THREEPLACES))
		self.assertEquals(loan.disbursement_date.year, 2018)
		self.assertEquals(loan.disbursement_date.month, 1)
		self.assertEquals(loan.disbursement_date.day, 1)

	def test_post_loan_error(self):
		response = client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_not_quota),
			content_type='application/json',
			**get_auth_header()
		)

		self.assertEquals(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
		self.assertEquals(response.data['message'],'User does not have available quota')
		self.assertEquals(len(Loan.objects.filter(user_id = 1)),0)

	def test_get_loans(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_5),
			content_type='application/json',
			**get_auth_header()
		)
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header()
		)
		user = User.objects.create(
			id = 2,
			full_name = 'Foo Full Name',
			identification = 99899
		)
		UserAuth.objects.create(
			email = "mail_for_tests_2@mail.com",
			password = "pbkdf2_sha256$100000$GGXOHIxTaqdf$h8sarOioBKxABatTgcYXnpxVaCGS/8R5mzdFpp7gj08=",
			is_active = True,
			role = 1,
			user = user
		)
		UserFinance.objects.create(
			contributions= 2000,
			balance_contributions= 2000,
			total_quota= 1000,
			available_quota= 500,
			user= user
		)
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_20),
			content_type='application/json',
			**{'HTTP_AUTHORIZATION': "Basic bWFpbF9mb3JfdGVzdHNfMkBtYWlsLmNvbTpwYXNzd29yZA=="}
		)

		response = client.get(
			reverse(view_get_post_loans),
			**{'HTTP_AUTHORIZATION': "Basic bWFpbF9mb3JfdGVzdHNfMkBtYWlsLmNvbTpwYXNzd29yZA=="}	
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data),1)
		for loan in response.data:
			self.assertIsNotNone(loan['user_name'])
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
			**get_auth_header()
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data),2)
		for loan in response.data:
			self.assertIsNotNone(loan['user_name'])
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
			**get_auth_header()
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data),2)

		response = client.get(
			"%s?all_loans=true" % reverse(view_get_post_loans),
			**{'HTTP_AUTHORIZATION': "Basic bWFpbF9mb3JfdGVzdHNfMkBtYWlsLmNvbTpwYXNzd29yZA=="}	
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)
		self.assertEquals(len(response.data),3)

	def test_update_loan_state(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header()
		)

		loan = Loan.objects.get(user_id = 1)
		response = client.patch(
			reverse(view_update_loan,kwargs={'id': loan.id}),
			data = '{"state":2}',
			content_type='application/json',
			**get_auth_header()
		)
		self.assertEquals(response.status_code,status.HTTP_200_OK)

		loan = Loan.objects.get(user_id = 1)
		self.assertEquals(loan.state,2)
		self.assertEquals(loan.get_state_display(),'DENIED')

	def test_update_loan_not_found(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header()
		)

		loan = Loan.objects.get(user_id = 1)
		response = client.patch(
			reverse(view_update_loan,kwargs={'id': loan.id+1}),
			data = '{"state":2}',
			content_type='application/json',
			**get_auth_header()
		)
		self.assertEquals(response.status_code,status.HTTP_404_NOT_FOUND)
		self.assertEquals(response.data['message'],'Loan does not exist')

	def test_update_loan_exceeded(self):
		client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**get_auth_header()
		)

		loan = Loan.objects.get(user_id = 1)
		response = client.patch(
			reverse(view_update_loan,kwargs={'id': loan.id+1}),
			data = '{"state":5}',
			content_type='application/json',
			**get_auth_header()
		)
		self.assertEquals(response.status_code,status.HTTP_400_BAD_REQUEST)
		self.assertEquals(response.data['message'],'State must be less or equal than 3')