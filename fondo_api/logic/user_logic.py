from ..models import UserProfile,UserFinance
from django.contrib.auth.models import User
from django.db import IntegrityError,transaction
from rest_framework.authtoken.models import Token 
from ..serializers import UserProfileSerializer

def create_user(obj):
	with transaction.atomic():
		try:
			user = UserProfile.objects.create_user(
				identification = obj['identification'],
				role = obj['role'],
				first_name = obj['first_name'],
				last_name = obj['last_name'],
				email = obj['email'],
				username = obj['email']
			)
		except IntegrityError:
			return (False,'Identification/email already exists')
		UserFinance.objects.create(
			contributions = obj['contributions'],
			balance_contributions = obj['balance_contributions'],
			total_quota = obj['total_quota'],
			available_quota = obj['available_quota'],
			user = user
		)
	#Send email to set password or next login?
	return (True,'Success')

def get_users():
	users = UserProfile.objects.all()
	serializer = UserProfileSerializer(users,many=True)
	return serializer.data

def get_user(id):
	try:
		user_finance = UserFinance.objects.get(user_id = id)
	except UserFinance.DoesNotExist:
		return (False,{})
	user = user_finance.user
	return (True,{
		'id': user.id,
		'identification': user.identification,
		'full_name': ''.join([user.first_name,' ',user.last_name]),
		'email': user.email,
		'role': user.get_role_display(),
		'contributions': user_finance.contributions,
		'balance_contributions': user_finance.balance_contributions,
		'total_quota': user_finance.total_quota,
		'available_quota': user_finance.available_quota
	})

def delete_token(user_id):
	try:
		Token.objects.get(user_id = user_id).delete()
	except Token.DoesNotExist:
		return False
	return True

def inactive_user(id):
	try:
		user = User.objects.get(id = id)
	except User.DoesNotExist:
		return False
	user.is_active = False
	user.save()
	return True