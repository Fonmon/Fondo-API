from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from ..models import User,UserAuth,UserFinance,Loan
from datetime import datetime, date, time

class UserTest(TestCase):

	def setUp(self):
		User.objects.create(
			full_name = 'Foo Full Name',
			identification = 1234567890
		)

	def test_unique_identification(self):
		#Repeated identification
		try:
			User.objects.create(
				full_name = 'Foo Full Name 2',
				identification = 1234567890
			)
			self.fail('identification must be unique')
		except IntegrityError:
			pass

class UserAuthTest(TestCase):

	def setUp(self):
		user = User.objects.create(
			full_name = 'Foo Full Name',
			identification = 1234567890
		)
		UserAuth.objects.create(
			email = "mail@email.com",
			user = user
		)

	def test_default_values(self):
		user = User.objects.get(identification = 1234567890)
		userAuth = UserAuth.objects.get(user_id = user.id)
		self.assertEqual(userAuth.role,3)
		self.assertEqual(userAuth.get_role_display(),'MEMBER')
		self.assertEqual(userAuth.is_active,False)
		self.assertEqual(userAuth.is_authenticated,True)
		self.assertEqual(userAuth.password,'')

	def test_unique_email(self):
		user = User.objects.create(
			full_name = 'Foo Full Name 2',
			identification = 123450
		)
		try:
			UserAuth.objects.create(
				email = "mail@email.com",
				user = user
			)
			self.fail('email must be unique')
		except IntegrityError:
			pass

class LoanTest(TestCase):

	def setUp(self):
		user = User.objects.create(
			full_name = 'Foo Full Name',
			identification = 1234567890
		)
		foo_date = date(2017, 12, 9)
		foo_time = time(12, 0, 0, tzinfo=timezone.get_current_timezone())
		aware_datetime = datetime.combine(foo_date, foo_time)
		Loan.objects.create(
			value = 0,
			fee = 1,
			timelimit = aware_datetime,
			disbursement_date = aware_datetime,
			user = user
		)

	def test_default_values(self):
		user = User.objects.get(identification = 1234567890)
		loan = Loan.objects.get(user_id = user.id)
		foo_date = date(2017, 12, 9)
		foo_time = time(12, 0, 0, tzinfo=timezone.get_current_timezone())
		aware_datetime = datetime.combine(foo_date, foo_time)

		self.assertEqual(loan.value,0)
		self.assertEqual(loan.fee,1)
		self.assertEqual(loan.get_fee_display(),'UNIQUE')
		self.assertIsNotNone(loan.timelimit)
		self.assertIsNotNone(loan.disbursement_date)
		self.assertEqual(loan.disbursement_date,aware_datetime)
		self.assertIsNotNone(loan.created_at)
		self.assertEqual(loan.state,0)
		self.assertEqual(loan.get_state_display(),'WAITING_APPROVAL')

	def test_many_loans(self):
		user = User.objects.get(identification = 1234567890)
		foo_date = date(2016, 12, 9)
		foo_time = time(12, 0, 0, tzinfo=timezone.get_current_timezone())
		aware_datetime = datetime.combine(foo_date, foo_time)
		Loan.objects.create(
			value = 1000,
			fee = 0,
			timelimit = aware_datetime,
			disbursement_date = aware_datetime,
			user = user
		)

		loans = Loan.objects.filter(user_id = user.id)
		self.assertEqual(len(loans),2)

		loans = Loan.objects.filter(timelimit__year = 2016)
		self.assertEqual(len(loans),1)