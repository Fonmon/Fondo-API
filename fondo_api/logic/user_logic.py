from ..models import User,UserAuth,UserFinance
from django.db import IntegrityError,transaction
from ..serializers import UserAuthSerializer

def create_user(obj):
	try:
		with transaction.atomic():
			try:
				user = User.objects.create(
					full_name = obj['full_name'],
					identification = obj['identification']
				)
			except IntegrityError:
				return (False,'Identification already exists')
			UserAuth.objects.create(
				email = obj['email'],
				role = obj['role'],
				user = user
			)
			UserFinance.objects.create(
				contributions = obj['contributions'],
				balance_contributions = obj['balance_contributions'],
				total_quota = obj['total_quota'],
				available_quota = obj['available_quota'],
				user = user
			)
		#Send email to set password or next login?
		return (True,'Success')
	except IntegrityError:
		return (False,'Email already exists')

def get_users():
	users_auth = UserAuth.objects.all()
	serializer = UserAuthSerializer(users_auth,many=True)
	return serializer.data

def get_user(id):
	try:
		user_auth = UserAuth.objects.get(user_id = id)
	except UserAuth.DoesNotExist:
		return (False,{})
	user_finance = UserFinance.objects.get(user_id = id)
	user = user_auth.user
	return (True,{
		'id': user.id,
		'identification': user.identification,
		'full_name': user.full_name,
		'email': user_auth.email,
		'role': user_auth.get_role_display(),
		'contributions': user_finance.contributions,
		'balance_contributions': user_finance.balance_contributions,
		'total_quota': user_finance.total_quota,
		'available_quota': user_finance.available_quota
	})
