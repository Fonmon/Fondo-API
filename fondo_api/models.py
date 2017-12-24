from django.db import models
from django.contrib.auth.models import User

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

class UserFinance(models.Model):
	contributions = models.BigIntegerField()
	balance_contributions = models.BigIntegerField()
	total_quota = models.BigIntegerField()
	available_quota = models.BigIntegerField()
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
		(1,'BANK_ACCOUNT')
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