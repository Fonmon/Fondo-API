import json
from .abstract_test import AbstractTest
from ..models import *
from django.urls import reverse
from django.core import mail
from django.test.client import encode_multipart
from rest_framework import status
from decimal import Decimal

view_get_update_loan = 'view_get_update_loan'
view_get_post_loans = 'view_get_post_loans'
view_loan_apps = 'view_loan_apps'

class LoanViewTest(AbstractTest):
	def setUp(self):
		self.create_user()
		self.token = self.get_token('mail_for_tests@mail.com','password')
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
		response = self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_5),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		loan = Loan.objects.get(user_id = 1)
		self.assertEqual(response.data['id'],loan.id)
		self.assertEqual(loan.value,100)
		self.assertEqual(loan.get_fee_display(),'MONTHLY')
		self.assertEqual(loan.get_state_display(),'WAITING_APPROVAL')
		self.assertEqual(loan.rate,Decimal(0.02).quantize(self.THREEPLACES))
		self.assertEqual(loan.disbursement_date.year, 2017)
		self.assertEqual(loan.disbursement_date.month, 12)
		self.assertEqual(loan.disbursement_date.day, 9)
		self.assertEqual(loan.comments,'')
		self.assertEqual(loan.payment,0)
		self.assertEqual(loan.get_payment_display(),'CASH')

	def test_post_loan_2(self):
		response = self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		loan = Loan.objects.get(user_id = 1)
		self.assertEqual(response.data['id'],loan.id)
		self.assertEqual(loan.value,200)
		self.assertEqual(loan.get_fee_display(),'MONTHLY')
		self.assertEqual(loan.get_state_display(),'WAITING_APPROVAL')
		self.assertEqual(loan.rate,Decimal(0.025).quantize(self.THREEPLACES))
		self.assertEqual(loan.disbursement_date.year, 2017)
		self.assertEqual(loan.disbursement_date.month, 11)
		self.assertEqual(loan.disbursement_date.day, 9)
		self.assertEqual(loan.comments,'')
		self.assertEqual(loan.payment,1)
		self.assertEqual(loan.get_payment_display(),'BANK_ACCOUNT')

	def test_post_loan_3(self):
		response = self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_20),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		loan = Loan.objects.get(user_id = 1)
		self.assertEqual(response.data['id'],loan.id)
		self.assertEqual(loan.value,300)
		self.assertEqual(loan.get_fee_display(),'MONTHLY')
		self.assertEqual(loan.get_state_display(),'WAITING_APPROVAL')
		self.assertEqual(loan.rate,Decimal(0.03).quantize(self.THREEPLACES))
		self.assertEqual(loan.disbursement_date.year, 2018)
		self.assertEqual(loan.disbursement_date.month, 1)
		self.assertEqual(loan.disbursement_date.day, 1)
		self.assertEqual(loan.comments,'')
		self.assertEqual(loan.payment,0)
		self.assertEqual(loan.get_payment_display(),'CASH')

	def test_post_loan_error(self):
		response = self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_not_quota),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
		self.assertEqual(response.data['message'],'User does not have available quota')
		self.assertEqual(len(Loan.objects.filter(user_id = 1)),0)

	def test_get_loans_paginator(self):
		for i in range(25):
			self.client.post(
				reverse(view_get_post_loans),
				data = json.dumps(self.loan_with_quota_fee_5),
				content_type='application/json',
				**self.get_auth_header(self.token)
			)
		self.assertEqual(len(Loan.objects.all()),25)
		response = self.client.get(
			reverse(view_get_post_loans),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),10)
		self.assertEqual(response.data['num_pages'],3)
		response = self.client.get(
			"%s?page=0" % reverse(view_get_post_loans),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response.data['message'],'Page number must be greater or equal than 0')
		response = self.client.get(
			"%s?page=3" % reverse(view_get_post_loans),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),5)
		self.assertEqual(response.data['num_pages'],3)

		response = self.client.get(
			"%s?page=4" % reverse(view_get_post_loans),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),0)
		self.assertEqual(response.data['num_pages'],3)

	def test_get_loans_not_paginator(self):
		for i in range(25):
			self.client.post(
				reverse(view_get_post_loans),
				data = json.dumps(self.loan_with_quota_fee_5),
				content_type='application/json',
				**self.get_auth_header(self.token)
			)
		self.assertEqual(len(Loan.objects.all()),25)
		response = self.client.get(
			"%s?paginate=false" % reverse(view_get_post_loans),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),25)
		self.assertFalse(hasattr(response.data,'num_pages'))

	def test_get_loans(self):
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_5),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
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
		token = self.get_token('mail_for_tests_2@mail.com','password')
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_20),
			content_type='application/json',
			**self.get_auth_header(token)
		)

		response = self.client.get(
			reverse(view_get_post_loans),
			**self.get_auth_header(token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),1)
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

		response = self.client.get(
			reverse(view_get_post_loans),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),2)
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

		response = self.client.get(
			"%s?all_loans=true" % reverse(view_get_post_loans),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),3)

		response = self.client.get(
			"%s?all_loans=true" % reverse(view_get_post_loans),
			**self.get_auth_header(token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),1)

	def test_get_loans_filter(self):
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_5),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		response = self.client.get(
			"%s?state=5" % reverse(view_get_post_loans),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response.data['message'],'State must be between 0 and 4')

		response = self.client.get(
			"%s?state=1" % reverse(view_get_post_loans),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),0)

		response = self.client.get(
			"%s?state=0" % reverse(view_get_post_loans),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),2)
		for loan in response.data['list']:
			self.assertEqual(loan['state'],0)

	def test_get_loans_filter_all(self):
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_5),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		response = self.client.get(
			"%s?state=0&all_loans=true" % reverse(view_get_post_loans),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(response.data['list']),2)
		for loan in response.data['list']:
			self.assertEqual(loan['state'],0)

	def test_update_loan_approved_monthly(self):
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = self.client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":1}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(response.data['total_payment'],228)
		self.assertEqual(response.data['minimum_payment'],25)
		self.assertEqual(response.data['payday_limit'],'9 dic. 2017')
		self.assertEqual(len(mail.outbox),1)
		self.assertEqual(mail.outbox[0].subject,'[Fondo Montañez] Solicitud de crédito')
		self.assertEqual(len(mail.outbox[0].to),1)
		self.assertEqual(mail.outbox[0].to[0],'mail_for_tests@mail.com')
		content = mail.outbox[0].body
		mimetype = mail.outbox[0].content_subtype
		self.assertEqual(mimetype,'html')
		subcontent = 'crédito número: {},'.format(loan.id)
		self.assertTrue(subcontent in content)
		subcontent = '<strong>APROBADA</strong>'
		self.assertTrue(subcontent in content)
		subcontent = '<table style="width:100%" border="1"><tr><th>Cuota</th><th>Saldo inicial</th><th>Fecha inicial</th><th>Intereses</th><th>Abono a capital</th><th>Fecha de pago</th><th>Valor pago</th><th>Saldo final</th></tr><tr><td>1</td><td>$200</td><td>9 nov. 2017</td><td>$5</td><td>$20</td><td>9 dic. 2017</td><td>$25</td><td>$180</td></tr><tr><td>2</td><td>$180</td><td>9 dic. 2017</td><td>$4</td><td>$20</td><td>9 ene. 2018</td><td>$24</td><td>$160</td></tr><tr><td>3</td><td>$160</td><td>9 ene. 2018</td><td>$4</td><td>$20</td><td>9 feb. 2018</td><td>$24</td><td>$140</td></tr><tr><td>4</td><td>$140</td><td>9 feb. 2018</td><td>$3</td><td>$20</td><td>9 mar. 2018</td><td>$23</td><td>$120</td></tr><tr><td>5</td><td>$120</td><td>9 mar. 2018</td><td>$3</td><td>$20</td><td>9 abr. 2018</td><td>$23</td><td>$100</td></tr><tr><td>6</td><td>$100</td><td>9 abr. 2018</td><td>$2</td><td>$20</td><td>9 may. 2018</td><td>$22</td><td>$80</td></tr><tr><td>7</td><td>$80</td><td>9 may. 2018</td><td>$2</td><td>$20</td><td>9 jun. 2018</td><td>$22</td><td>$60</td></tr><tr><td>8</td><td>$60</td><td>9 jun. 2018</td><td>$1</td><td>$20</td><td>9 jul. 2018</td><td>$21</td><td>$40</td></tr><tr><td>9</td><td>$40</td><td>9 jul. 2018</td><td>$1</td><td>$20</td><td>9 ago. 2018</td><td>$21</td><td>$20</td></tr><tr><td>10</td><td>$20</td><td>9 ago. 2018</td><td>$0</td><td>$20</td><td>9 sept. 2018</td><td>$20</td><td>$0</td></tr></table>'
		self.assertTrue(subcontent in content)

		loan = Loan.objects.get(user_id = 1)
		self.assertEqual(loan.state,1)
		self.assertEqual(loan.get_state_display(),'APPROVED')

		response = self.client.get(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['loan']['id'],loan.id)
		self.assertEqual(response.data['loan']['value'],200)
		self.assertEqual(response.data['loan']['timelimit'],10)
		self.assertEqual(response.data['loan']['disbursement_date'],'9 nov. 2017')
		self.assertEqual(response.data['loan']['payment'],1)
		self.assertEqual(response.data['loan']['fee'],0)
		self.assertEqual(response.data['loan']['comments'],'')
		self.assertEqual(response.data['loan']['state'],1)
		self.assertEqual(response.data['loan']['user_full_name'],'Foo Name Foo Last Name')
		self.assertEqual(Decimal(response.data['loan']['rate']).quantize(self.THREEPLACES),Decimal(0.025).quantize(self.THREEPLACES))
		self.assertIsNotNone(response.data['loan']['created_at'])

		self.assertEqual(response.data['loan_detail']['total_payment'],228)
		self.assertEqual(response.data['loan_detail']['minimum_payment'],25)
		self.assertEqual(response.data['loan_detail']['payday_limit'],'9 dic. 2017')
		self.assertEqual(response.data['loan_detail']['from_date'],'9 nov. 2017')

	def test_update_loan_approved_unique(self):
		self.loan_with_quota_fee_10['fee']=1
		self.loan_with_quota_fee_10['timelimit']=13
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = self.client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":1}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(response.data['total_payment'],278)
		self.assertEqual(response.data['minimum_payment'],278)
		self.assertEqual(response.data['payday_limit'],'9 dic. 2018')
		self.assertEqual(len(mail.outbox),1)
		self.assertEqual(mail.outbox[0].subject,'[Fondo Montañez] Solicitud de crédito')
		self.assertEqual(len(mail.outbox[0].to),1)
		self.assertEqual(mail.outbox[0].to[0],'mail_for_tests@mail.com')
		content = mail.outbox[0].body
		mimetype = mail.outbox[0].content_subtype
		self.assertEqual(mimetype,'html')
		subcontent = 'crédito número: {},'.format(loan.id)
		self.assertTrue(subcontent in content)
		subcontent = '<strong>APROBADA</strong>'
		self.assertTrue(subcontent in content)
		subcontent = '<table style="width:100%" border="1"><tr><th>Cuota</th><th>Saldo inicial</th><th>Fecha inicial</th><th>Intereses</th><th>Abono a capital</th><th>Fecha de pago</th><th>Valor pago</th><th>Saldo final</th></tr><tr><td>1</td><td>$200</td><td>9 nov. 2017</td><td>$78</td><td>$200</td><td>9 dic. 2018</td><td>$278</td><td>$0</td></tr></table>'
		self.assertTrue(subcontent in content)

		loan = Loan.objects.get(user_id = 1)
		self.assertEqual(loan.state,1)
		self.assertEqual(loan.get_state_display(),'APPROVED')

		response = self.client.get(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['loan']['id'],loan.id)
		self.assertEqual(response.data['loan']['value'],200)
		self.assertEqual(response.data['loan']['timelimit'],13)
		self.assertEqual(response.data['loan']['disbursement_date'],'9 nov. 2017')
		self.assertEqual(response.data['loan']['payment'],1)
		self.assertEqual(response.data['loan']['fee'],1)
		self.assertEqual(response.data['loan']['comments'],'')
		self.assertEqual(response.data['loan']['state'],1)
		self.assertEqual(response.data['loan']['user_full_name'],'Foo Name Foo Last Name')
		self.assertEqual(Decimal(response.data['loan']['rate']).quantize(self.THREEPLACES),Decimal(0.03).quantize(self.THREEPLACES))
		self.assertIsNotNone(response.data['loan']['created_at'])

		self.assertEqual(response.data['loan_detail']['total_payment'],278)
		self.assertEqual(response.data['loan_detail']['minimum_payment'],278)
		self.assertEqual(response.data['loan_detail']['payday_limit'],'9 dic. 2018')
		self.assertEqual(response.data['loan_detail']['from_date'],'9 nov. 2017')

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
		token = self.get_token('mail_for_tests_2@mail.com','password')

		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(token)
		)

		loan = Loan.objects.get(user_id = 2)
		response = self.client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":1}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(response.data['total_payment'],278)
		self.assertEqual(response.data['minimum_payment'],278)
		self.assertEqual(response.data['payday_limit'],'9 dic. 2018')
		self.assertEqual(len(mail.outbox),1)
		self.assertEqual(mail.outbox[0].subject,'[Fondo Montañez] Solicitud de crédito')
		self.assertEqual(len(mail.outbox[0].to),1)
		self.assertEqual(len(mail.outbox[0].bcc),1)
		self.assertEqual(mail.outbox[0].to[0],'mail_for_tests_2@mail.com')
		self.assertEqual(mail.outbox[0].bcc[0],'mail_for_tests@mail.com')
		content = mail.outbox[0].body
		mimetype = mail.outbox[0].content_subtype
		self.assertEqual(mimetype,'html')
		subcontent = 'crédito número: {},'.format(loan.id)
		self.assertTrue(subcontent in content)
		subcontent = '<strong>APROBADA</strong>'
		self.assertTrue(subcontent in content)
		subcontent = '<table style="width:100%" border="1"><tr><th>Cuota</th><th>Saldo inicial</th><th>Fecha inicial</th><th>Intereses</th><th>Abono a capital</th><th>Fecha de pago</th><th>Valor pago</th><th>Saldo final</th></tr><tr><td>1</td><td>$200</td><td>9 nov. 2017</td><td>$78</td><td>$200</td><td>9 dic. 2018</td><td>$278</td><td>$0</td></tr></table>'
		self.assertTrue(subcontent in content)

		loan = Loan.objects.get(user_id = 2)
		self.assertEqual(loan.state,1)
		self.assertEqual(loan.get_state_display(),'APPROVED')

	def test_update_loan_state(self):
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = self.client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":3}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)

		loan = Loan.objects.get(user_id = 1)
		self.assertEqual(loan.state,3)
		self.assertEqual(loan.get_state_display(),'PAID_OUT')

	def test_update_loan_denied(self):
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = self.client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":2}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(mail.outbox),1)
		self.assertEqual(mail.outbox[0].subject,'[Fondo Montañez] Solicitud de crédito')
		self.assertEqual(len(mail.outbox[0].to),1)
		self.assertEqual(mail.outbox[0].to[0],'mail_for_tests@mail.com')
		content = mail.outbox[0].body
		mimetype = mail.outbox[0].content_subtype
		self.assertEqual(mimetype,'html')
		subcontent = 'crédito número: {},'.format(loan.id)
		self.assertTrue(subcontent in content)
		subcontent = '<strong>RECHAZADA</strong>'
		self.assertTrue(subcontent in content)

		loan = Loan.objects.get(user_id = 1)
		self.assertEqual(loan.state,2)
		self.assertEqual(loan.get_state_display(),'DENIED')

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
		token = self.get_token('mail_for_tests_2@mail.com','password')

		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(token)
		)

		loan = Loan.objects.get(user_id = 2)
		response = self.client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":2}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_200_OK)
		self.assertEqual(len(mail.outbox),1)
		self.assertEqual(mail.outbox[0].subject,'[Fondo Montañez] Solicitud de crédito')
		self.assertEqual(len(mail.outbox[0].to),1)
		self.assertEqual(len(mail.outbox[0].bcc),1)
		self.assertEqual(mail.outbox[0].to[0],'mail_for_tests_2@mail.com')
		self.assertEqual(mail.outbox[0].bcc[0],'mail_for_tests@mail.com')
		content = mail.outbox[0].body
		mimetype = mail.outbox[0].content_subtype
		self.assertEqual(mimetype,'html')
		subcontent = 'crédito número: {},'.format(loan.id)
		self.assertTrue(subcontent in content)
		subcontent = '<strong>RECHAZADA</strong>'
		self.assertTrue(subcontent in content)

		loan = Loan.objects.get(user_id = 2)
		self.assertEqual(loan.state,2)
		self.assertEqual(loan.get_state_display(),'DENIED')

	def test_update_loan_not_found(self):
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = self.client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id+1}),
			data = '{"state":2}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)
		self.assertEqual(response.data['message'],'Loan does not exist')

	def test_update_loan_exceeded(self):
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		loan = Loan.objects.get(user_id = 1)
		response = self.client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id+1}),
			data = '{"state":5}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response.data['message'],'State must be less or equal than 3')

	def test_get_loan(self):
		self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		loan = Loan.objects.get(user_id = 1)

		response = self.client.get(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['loan']['id'],loan.id)
		self.assertEqual(response.data['loan']['value'],200)
		self.assertEqual(response.data['loan']['timelimit'],10)
		self.assertEqual(response.data['loan']['disbursement_date'],'9 nov. 2017')
		self.assertEqual(response.data['loan']['payment'],1)
		self.assertEqual(response.data['loan']['fee'],0)
		self.assertEqual(response.data['loan']['comments'],'')
		self.assertEqual(response.data['loan']['state'],0)
		self.assertEqual(response.data['loan']['user_full_name'],'Foo Name Foo Last Name')
		self.assertEqual(Decimal(response.data['loan']['rate']).quantize(self.THREEPLACES),Decimal(0.025).quantize(self.THREEPLACES))
		self.assertIsNotNone(response.data['loan']['created_at'])

	def test_get_loan_not_found(self):
		response = self.client.get(
			reverse(view_get_update_loan,kwargs={'id': 2}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def create_test_file(self):
		try:
			file = open("testfile.txt","w")
			file.write("1\t1234\t5678\t1/1/2018\t13\t24\t2/2/2018\r\n")
			file.write("2\t4321\t8765\t2/1/2018\t45\t56\t3/3/2018\r\n")
			file.write("3\t1\t2\t3/1/2017\t4\t5\t1/1/2017\r\n")
			file.write("5\t1\t2\t3/1/2017\t4\t5\t3/3/2017\r\n")
		finally:
			file.close()
		return file

	def test_bulk_update_loans(self):
		user = UserProfile.objects.get(id=1)
		for i in range(4):
			loan = Loan.objects.create(
				id=i+1,
				value=100,
				timelimit= 5,
				disbursement_date= '2000-1-1',
				comments='',
				payment=0,
				state=1,
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
		response = self.client.patch(
			reverse(view_get_post_loans),
			data=encode_multipart('file',file),
			content_type='multipart/form-data; boundary=file',
			**self.get_auth_header(self.token)
		)

		self.assertEqual(response.status_code,status.HTTP_200_OK)

		loan_detail = LoanDetail.objects.get(loan_id=1)
		self.assertEqual(loan_detail.total_payment,1234)
		self.assertEqual(loan_detail.minimum_payment,5678)
		self.assertEqual(loan_detail.payday_limit.year,2018)
		self.assertEqual(loan_detail.payday_limit.month,1)
		self.assertEqual(loan_detail.payday_limit.day,1)
		self.assertEqual(loan_detail.interests,13)
		self.assertEqual(loan_detail.capital_balance,24)
		self.assertEqual(loan_detail.from_date.year,2018)
		self.assertEqual(loan_detail.from_date.month,2)
		self.assertEqual(loan_detail.from_date.day,2)
		self.assertEqual(loan_detail.loan.state, 1)

		loan_detail = LoanDetail.objects.get(loan_id=2)
		self.assertEqual(loan_detail.total_payment,4321)
		self.assertEqual(loan_detail.minimum_payment,8765)
		self.assertEqual(loan_detail.payday_limit.year,2018)
		self.assertEqual(loan_detail.payday_limit.month,1)
		self.assertEqual(loan_detail.payday_limit.day,2)
		self.assertEqual(loan_detail.interests,45)
		self.assertEqual(loan_detail.capital_balance,56)
		self.assertEqual(loan_detail.from_date.year,2018)
		self.assertEqual(loan_detail.from_date.month,3)
		self.assertEqual(loan_detail.from_date.day,3)
		self.assertEqual(loan_detail.loan.state, 1)

		loan_detail = LoanDetail.objects.get(loan_id=3)
		self.assertEqual(loan_detail.total_payment,1)
		self.assertEqual(loan_detail.minimum_payment,2)
		self.assertEqual(loan_detail.payday_limit.year,2017)
		self.assertEqual(loan_detail.payday_limit.month,1)
		self.assertEqual(loan_detail.payday_limit.day,3)
		self.assertEqual(loan_detail.interests,4)
		self.assertEqual(loan_detail.capital_balance,5)
		self.assertEqual(loan_detail.from_date.year,2017)
		self.assertEqual(loan_detail.from_date.month,1)
		self.assertEqual(loan_detail.from_date.day,1)
		self.assertEqual(loan_detail.loan.state, 1)

		loan_detail = LoanDetail.objects.get(loan_id=3)
		self.assertEqual(loan_detail.loan.state, 1)

	def test_loan_app_not_found(self):
		response = self.client.post(
			reverse(view_loan_apps,kwargs={'id': 2,'app':'notFound'}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

	def test_payment_projection_date_none(self):
		response = self.client.post(
			reverse(view_loan_apps,kwargs={'id': 1,'app':'paymentProjection'}),
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

	def test_payment_projection(self):
		response = self.client.post(
			reverse(view_get_post_loans),
			data = json.dumps(self.loan_with_quota_fee_10),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		loan = Loan.objects.get(user_id = 1)
		response = self.client.patch(
			reverse(view_get_update_loan,kwargs={'id': loan.id}),
			data = '{"state":1}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)

		response = self.client.post(
			reverse(view_loan_apps,kwargs={'id': loan.id,'app':'paymentProjection'}),
			data='{"to_date":"2017-11-09"}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['capital_balance'],200)
		self.assertEqual(response.data['interests'],0)

		response = self.client.post(
			reverse(view_loan_apps,kwargs={'id': loan.id,'app':'paymentProjection'}),
			data='{"to_date":"2017-11-15"}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['capital_balance'],200)
		self.assertEqual(response.data['interests'],1)

		response = self.client.post(
			reverse(view_loan_apps,kwargs={'id': loan.id,'app':'paymentProjection'}),
			data='{"to_date":"2017-12-09"}',
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['capital_balance'],200)
		self.assertEqual(response.data['interests'],5)