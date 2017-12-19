from django.test import TestCase
from django.db import IntegrityError
from ..models import UserProfile,UserFinance,Loan
from datetime import date

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