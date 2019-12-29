from django.db import models
from django.contrib.postgres.fields import HStoreField
from django.contrib.auth.models import User
from datetime import date

class UserProfile(User):
	REQUIRED_FIELDS = ('email','password')
	ROLES = (
		(0,'ADMIN'),
		(1,'PRESIDENT'),
		(2,'TREASURER'),
		(3,'MEMBER')
	)
	USERNAME_FIELD = 'email'
	identification = models.BigIntegerField(unique=True)
	role = models.IntegerField(choices=ROLES,default=3)
	key_activation = models.CharField(null=True,max_length=100)

class UserPreference(models.Model):
	notifications = models.BooleanField(default=False)
	primary_color = models.CharField(max_length=15, default="#800000")
	secondary_color = models.CharField(max_length=15, default="#c83737")
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

class UserFinance(models.Model):
	contributions = models.BigIntegerField()
	balance_contributions = models.BigIntegerField()
	total_quota = models.BigIntegerField()
	utilized_quota = models.BigIntegerField(default=0)
	available_quota = models.BigIntegerField()
	last_modified = models.DateField(auto_now=True)
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

class Loan(models.Model):
	LOAN_STATES = (
		(0,'WAITING_APPROVAL'),
		(1,'APPROVED'),
		(2,'DENIED'),
		(3,'PAID_OUT')
	)
	FEE_TYPES = (
		(0,'MONTHLY'),
		(1,'UNIQUE')
	)
	PAYMENT_TYPES = (
		(0,'CASH'),
		(1,'BANK_ACCOUNT'),
		(2,'REFINANCED')
	)
	value = models.BigIntegerField()
	timelimit = models.IntegerField()
	disbursement_date = models.DateField()
	payment = models.IntegerField(choices=PAYMENT_TYPES, default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	fee = models.IntegerField(choices=FEE_TYPES)
	comments = models.TextField(null=True)
	state = models.IntegerField(choices=LOAN_STATES, default=0)
	rate = models.DecimalField(max_digits=5,decimal_places=3)
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	prev_loan = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
	refinanced_loan = models.BigIntegerField(null=True)
	disbursement_value = models.BigIntegerField(null = True)

class LoanDetail(models.Model):
	total_payment = models.BigIntegerField(default = 0)
	minimum_payment = models.BigIntegerField(default = 0)
	payday_limit = models.DateField()
	interests = models.BigIntegerField(default = 0)
	capital_balance = models.BigIntegerField(default = 0)
	from_date = models.DateField(default = date.today)
	loan = models.ForeignKey(Loan, on_delete=models.CASCADE)

class ActivityYear(models.Model):
	year = models.BigIntegerField(default = 0, unique=True)
	enable = models.BooleanField(default = True)

class Activity(models.Model):
	name = models.TextField(default="")
	value = models.BigIntegerField(default=0)
	date = models.DateField()
	year = models.ForeignKey(ActivityYear, on_delete=models.CASCADE)
	users = models.ManyToManyField(UserProfile, through='ActivityUser')

class ActivityUser(models.Model):
	STATE_TYPES = (
		(0,'NOT_PAID'),
		(1,'PAID_OUT'),
		(2,'EXEMPTED')
	)
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	activity = models.ForeignKey(Activity,on_delete=models.CASCADE)
	state = models.IntegerField(choices=STATE_TYPES, default=0)

class NotificationSubscriptions(models.Model):
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	subscription = HStoreField()