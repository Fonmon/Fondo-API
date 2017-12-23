from ..models import UserProfile,UserFinance
from django.contrib.auth.models import User
from django.db import IntegrityError,transaction
from rest_framework.authtoken.models import Token 
from django.core.paginator import Paginator
from ..serializers import UserProfileSerializer

USERS_PER_PAGE = 10

def create_user(obj):
	with transaction.atomic():
		try:
			user = UserProfile.objects.create_user(
				identification = obj['identification'],
				role = obj['role'],
				first_name = obj['first_name'],
				last_name = obj['last_name'],
				email = obj['email'],
				username = obj['email'],
				is_active = False
			)
		except IntegrityError:
			return (False,'Identification/email already exists')
		UserFinance.objects.create(
			contributions = 0,
			balance_contributions = 0,
			total_quota = 0,
			available_quota = 0,
			user = user
		)
	#Send email to set password or next login?
	return (True,'Success')

def get_users(page=1):
	users = UserProfile.objects.filter(is_active = True).order_by('id')
	paginator = Paginator(users,USERS_PER_PAGE)
	if page > paginator.num_pages:
		return {'list':[], 'num_pages':paginator.num_pages}
	page_return = paginator.page(page)
	serializer = UserProfileSerializer(page_return.object_list,many=True)
	return {'list':serializer.data, 'num_pages':paginator.num_pages}

def get_user(id):
	try:
		user_finance = UserFinance.objects.get(user_id = id)
	except UserFinance.DoesNotExist:
		return (False,{})
	user = user_finance.user
	return (True,{
		'id': user.id,
		'identification': user.identification,
		'first_name': user.first_name,
		'last_name': user.last_name,
		'email': user.email,
		'role': user.role,
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

def update_user(id,obj):
	with transaction.atomic():
		try:
			user_finance = UserFinance.objects.get(user_id = id)
		except UserFinance.DoesNotExist:
			return (False,404)
		user = user_finance.user
		user_finance.contributions = obj['contributions']
		user_finance.balance_contributions = obj['balance_contributions']
		user_finance.total_quota = obj['total_quota']
		user_finance.available_quota = obj['available_quota'];
		user_finance.save()

		user.first_name = obj['first_name']
		user.last_name = obj['last_name']
		user.email = obj['email']
		user.username = obj['email']
		user.identification = obj['identification']
		user.role = obj['role']
		try:
			user.save()
		except IntegrityError:
			return (False,409)
	return (True,200)