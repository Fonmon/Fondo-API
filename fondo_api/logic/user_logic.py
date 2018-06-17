from ..models import UserProfile,UserFinance
from django.contrib.auth.models import User
from django.db import IntegrityError,transaction
from rest_framework.authtoken.models import Token 
from django.core.paginator import Paginator
from ..serializers import UserProfileSerializer
import binascii,os
import logging
from . import sender_mails

USERS_PER_PAGE = 10
logger = logging.getLogger(__name__)

def generate_key():
	return binascii.hexlify(os.urandom(25)).decode()

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
				key_activation = generate_key(),
				is_active = False
			)
		except IntegrityError:
			return (False,'Identification/email already exists')
		UserFinance.objects.create(
			contributions = 0,
			balance_contributions = 0,
			total_quota = 0,
			available_quota = 0,
			utilized_quota = 0,
			user = user
		)
		if not sender_mails.send_activation_mail(user):
			transaction.set_rollback(True)
			return (False, 'Invalid email');
	return (True,'Success')

def get_users(page=1):
	users = UserProfile.objects.filter(is_active = True).order_by('id')
	paginator = Paginator(users,USERS_PER_PAGE)
	if page > paginator.num_pages:
		return {'list':[], 'num_pages':paginator.num_pages}
	page_return = paginator.page(page)
	serializer = UserProfileSerializer(page_return.object_list,many=True)
	return {'list':serializer.data, 'num_pages':paginator.num_pages}

'''
TODO: make a serializer for returning this data
'''
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
		'available_quota': user_finance.available_quota,
		'utilized_quota': user_finance.utilized_quota,
		'last_modified': user_finance.last_modified.strftime("%d %b. %Y")
	})

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
			user = update_user_finance(id,None,obj);
		except UserFinance.DoesNotExist:
			return (False,404)
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

def update_user_finance(id,identification,obj):
	try:
		if id is not None:
			user_finance = UserFinance.objects.get(user_id = id)
		else:
			user_finance = UserFinance.objects.get(user__identification = identification)
	except UserFinance.DoesNotExist:
		raise
	if (user_finance.contributions != obj['contributions']
		or user_finance.balance_contributions != obj['balance_contributions']
		or user_finance.total_quota != obj['total_quota']
		or user_finance.utilized_quota != obj['utilized_quota']):
		user_finance.contributions = obj['contributions']
		user_finance.balance_contributions = obj['balance_contributions']
		user_finance.total_quota = obj['total_quota']
		user_finance.utilized_quota = obj['utilized_quota']
		user_finance.available_quota = int(user_finance.total_quota) - int(user_finance.utilized_quota)
		user_finance.save()
	return user_finance.user

def activate_user(id,obj):
	try:
		user = UserProfile.objects.get(
			id=id,
			key_activation=obj['key'],
			identification=obj['identification']
		)
	except UserProfile.DoesNotExist:
		return False
	user.set_password(obj['password'])
	user.is_active = True
	user.save()
	return True

'''
* identification
* balance_contributions
* total_quota
* contributions
* utilized_quota
'''
def bulk_update_users(obj):
	for line in obj['file']:
		data = line.decode('utf-8').strip().split("\t")
		info = {}
		identification = int(data[0])
		info['balance_contributions']=int(round(float(data[1]),0))
		info['total_quota']=int(round(float(data[2]),0))
		info['contributions']=int(round(float(data[3]),0))
		info['utilized_quota'] = int(round(float(data[4]),0))
		try:
			update_user_finance(None,identification,info)
		except UserFinance.DoesNotExist:
			logger.error('User with identification: {}, not exists'.format(identification))
			continue

def get_profile_emails(profiles):
	users = UserProfile.objects.filter(role__in = profiles)
	emails = []
	for user in users:
		emails.append(user.email)
	return emails