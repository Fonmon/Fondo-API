from django.db import models

class User(models.Model):
	full_name = models.CharField(max_length=255)
	identification = models.BigIntegerField(unique=True)

class UserAuth(models.Model):
	ROLES = (
		(0,'ADMIN'),
		(1,'PRESIDENT'),
		(2,'TREASURER'),
		(3,'MEMBER')
	)
	email = models.CharField(max_length=255,unique=True)
	password = models.CharField(max_length=255)
	role = models.IntegerField(choices=ROLES,default=3)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	# Values for auth.model.user
	## is_active's purpose: Set new password
	is_active = models.BooleanField(default=False)
	is_authenticated = models.BooleanField(default=True)

class UserFinance(models.Model):
	contributions = models.BigIntegerField()
	balance_contributions = models.BigIntegerField()
	total_quota = models.BigIntegerField()
	available_quota = models.BigIntegerField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)

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
	value = models.BigIntegerField()
	timelimit = models.DateTimeField()
	disbursement_date = models.DateTimeField()
	created_at = models.DateTimeField(auto_now_add=True)
	fee = models.IntegerField(choices=FEE_TYPES)
	state = models.IntegerField(choices=LOAN_STATES, default=0)
	user = models.ForeignKey(User, on_delete=models.CASCADE)