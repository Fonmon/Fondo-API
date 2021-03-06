from django.test import TestCase
from django.db import IntegrityError
from datetime import date

from fondo_api.models import *

class UserProfileTest(TestCase):

	def setUp(self):
		UserProfile.objects.create(
			first_name = 'Foo Name',
			last_name = 'Foo Last Name',
			username = 'username',
			identification = 1234567890
		)

	def test_unique_identification(self):
		#Repeated identification
		try:
			UserProfile.objects.create(
				first_name = 'Foo Name',
				last_name = 'Foo Last Name',
				username = 'username2',
				identification = 1234567890
			)
			self.fail('identification must be unique')
		except IntegrityError:
			pass

	# Username acts as email 
	def test_unique_username(self):
		#Repeated identification
		try:
			UserProfile.objects.create(
				first_name = 'Foo Name',
				last_name = 'Foo Last Name',
				username = 'username',
				identification = 123
			)
			self.fail('username must be unique')
		except IntegrityError:
			pass

	def test_default_values(self):
		user = UserProfile.objects.get(identification = 1234567890)
		self.assertEqual(user.role,3)
		self.assertEqual(user.get_role_display(),'MEMBER')
		self.assertEqual(user.password,'')
		self.assertIsNone(user.key_activation)

class LoanTest(TestCase):

	def setUp(self):
		user = UserProfile.objects.create(
			first_name = 'Foo Name',
			last_name = 'Foo Last Name',
			username = 'username',
			identification = 1234567890
		)
		foo_date = date(2017, 12, 9)
		Loan.objects.create(
			value = 0,
			fee = 1,
			timelimit = 5,
			disbursement_date = foo_date,
			rate = 0.004,
			user = user
		)

	def test_default_values(self):
		user = UserProfile.objects.get(identification = 1234567890)
		loan = Loan.objects.get(user_id = user.id)
		foo_date = date(2017, 12, 9)

		self.assertEqual(loan.value,0)
		self.assertEqual(loan.fee,1)
		self.assertEqual(loan.get_fee_display(),'UNIQUE')
		self.assertEqual(loan.timelimit,5)
		self.assertIsNotNone(loan.disbursement_date)
		self.assertEqual(loan.disbursement_date,foo_date)
		self.assertIsNotNone(loan.created_at)
		self.assertEqual(loan.state,0)
		self.assertEqual(loan.get_state_display(),'WAITING_APPROVAL')
		self.assertEqual(loan.payment,0)
		self.assertEqual(loan.get_payment_display(),'CASH')
		self.assertIsNone(loan.comments)
		self.assertIsNone(loan.prev_loan)
		self.assertIsNone(loan.refinanced_loan)
		self.assertIsNone(loan.disbursement_value)

	def test_many_loans(self):
		user = UserProfile.objects.get(identification = 1234567890)
		foo_date = date(2016, 12, 9)
		Loan.objects.create(
			value = 1000,
			fee = 0,
			timelimit = 5,
			rate = 0.004,
			disbursement_date = foo_date,
			user = user
		)

		loans = Loan.objects.filter(user_id = user.id)
		self.assertEqual(len(loans),2)

		loans = Loan.objects.filter(disbursement_date__year = 2016)
		self.assertEqual(len(loans),1)

class UserFinanceTest(TestCase):
	def setUp(self):
		UserProfile.objects.create(
			first_name = 'Foo Name',
			last_name = 'Foo Last Name',
			username = 'username',
			identification = 1234567890
		)

	def test_defaults(self):
		user = UserProfile.objects.get(identification = 1234567890)
		UserFinance.objects.create(
			contributions=123,
			balance_contributions=123,
			total_quota=124124,
			available_quota=41243,
			user = user
		)

		user_finance = UserFinance.objects.get(user_id=user.id)
		self.assertIsNotNone(user_finance)
		self.assertEqual(user_finance.utilized_quota,0)
		self.assertIsNotNone(user_finance.last_modified)

class LoanDetailTest(TestCase):

	def setUp(self):
		user = UserProfile.objects.create(
			first_name = 'Foo Name',
			last_name = 'Foo Last Name',
			username = 'username',
			identification = 1234567890
		)

	def test_loan_detail_defaults(self):
		user = UserProfile.objects.get(identification = 1234567890)
		foo_date = date(2016, 12, 9)
		loan = Loan.objects.create(
			value = 1000,
			fee = 0,
			timelimit = 5,
			rate = 0.004,
			disbursement_date = foo_date,
			user = user
		)
		LoanDetail.objects.create(
			payday_limit = foo_date,
			loan = loan
		)

		loan_detail = LoanDetail.objects.filter(loan_id = loan.id)
		self.assertIsNotNone(loan_detail)
		self.assertEqual(len(loan_detail),1)
		self.assertEqual(loan_detail[0].total_payment,0)
		self.assertEqual(loan_detail[0].minimum_payment,0)
		self.assertEqual(loan_detail[0].capital_balance,0)
		self.assertEqual(loan_detail[0].interests,0)
		self.assertIsNotNone(loan_detail[0].from_date)

	def test_delete_loan(self):
		user = UserProfile.objects.get(identification = 1234567890)
		foo_date = date(2016, 12, 9)
		loan = Loan.objects.create(
			value = 1000,
			fee = 0,
			timelimit = 5,
			rate = 0.004,
			disbursement_date = foo_date,
			user = user
		)
		Loan.objects.filter(id = loan.id).delete()
		loan_detail = LoanDetail.objects.filter(loan_id = loan.id)
		self.assertEqual(len(loan_detail),0)

class NotificationSubscriptionsTest(TestCase):

	def setUp(self):
		self.user = UserProfile.objects.create(
			first_name = 'Foo Name',
			last_name = 'Foo Last Name',
			username = 'username',
			identification = 1234567890
		)

	def pending_test_create_notification(self):
		notification = NotificationSubscriptions.objects.create(
			user = self.user,
			subscription = {
				'key1': 'value1',
				'key2': 'value2'
			}
		)

		self.assertEqual(notification.subscription['key1'], 'value1')
		self.assertEqual(notification.subscription['key2'], 'value2')

	def pending_test_query_notification(self):
		NotificationSubscriptions.objects.create(
			user = self.user,
			subscription = {
				'key1': 'value1',
				'key2': 'value2'
			}
		)

		notification = NotificationSubscriptions.objects.get( user_id = self.user.id )

		self.assertEqual(notification.subscription['key1'], 'value1')
		self.assertEqual(notification.subscription['key2'], 'value2')
		self.assertEqual(notification.user_id, self.user.id)