import binascii
import os
import logging
from django.contrib.auth.models import User
from django.db import IntegrityError,transaction
from django.core.paginator import Paginator
from django.conf import settings
from rest_framework.authtoken.models import Token 
from babel.dates import format_date

from fondo_api.models import UserProfile,UserFinance,UserPreference
from fondo_api.serializers import UserProfileSerializer, UserFullInfoSerializer
from fondo_api.logic import sender_mails
from fondo_api.logic import notifications_logic

USERS_PER_PAGE = 10
logger = logging.getLogger(__name__)

def generate_key():
	return binascii.hexlify(os.urandom(25)).decode()

def create_user(obj):
	try:
		with transaction.atomic():
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
			UserFinance.objects.create(
				contributions = 0,
				balance_contributions = 0,
				total_quota = 0,
				available_quota = 0,
				utilized_quota = 0,
				user = user
			)
			UserPreference.objects.create( user = user )
			if not sender_mails.send_activation_mail(user):
				transaction.set_rollback(True)
				return (False, 'Invalid email');
	except IntegrityError:
		return (False,'Identification/email already exists')
	return (True,'Success')

def get_users(page=1):
	users = UserProfile.objects.filter(is_active = True).order_by('id')
	paginator = Paginator(users,USERS_PER_PAGE)
	if page > paginator.num_pages:
		return {'list':[], 'num_pages':paginator.num_pages, 'count': paginator.count}
	page_return = paginator.page(page)
	serializer = UserProfileSerializer(page_return.object_list,many=True)
	return {'list':serializer.data, 'num_pages':paginator.num_pages, 'count': paginator.count}

def get_user(id):
	try:
		user_finance = UserFinance.objects.get(user_id = id)
		user_preference = UserPreference.objects.get(user_id = id)
	except:
		return (False,{})
	serializer = UserFullInfoSerializer((user_finance,user_preference))
	return (True, serializer.data)

def inactive_user(id):
	try:
		user = User.objects.get(id = id)
	except User.DoesNotExist:
		return False
	user.is_active = False
	user.save()
	return True

def update_user(id, obj):
	if obj['type'] == 'personal':
		return update_user_personal(id, obj['personal'])
	if obj['type'] == 'finance':
		return update_user_finance(id, None, obj['finance'])
	return update_user_preferences(id, obj['preferences'])

def update_user_preferences(id, obj):
	try:
		user_preference = UserPreference.objects.get(user_id = id)
		user_preference.notifications = obj['notifications']
		user_preference.save()
		if not user_preference.notifications:
			notifications_logic.remove_all_subscriptions(id)
	except:
		return (False, 404)
	return (True,200)

def update_user_personal(id, obj):
	try:
		with transaction.atomic():
			user = UserProfile.objects.get(id = id)
			user.first_name = obj['first_name']
			user.last_name = obj['last_name']
			user.email = obj['email']
			user.username = obj['email']
			user.identification = obj['identification']
			user.role = obj['role']
			user.save()
	except UserProfile.DoesNotExist:
		return (False,404)
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
		return (False,404)
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
	return (True,200)

def activate_user(id,obj):
	if 'key' not in obj or obj['key'] == '':
		return False
	try:
		user = UserProfile.objects.get(
			id=id,
			key_activation=obj['key'],
			identification=obj['identification']
		)
	except:
		return False
	user.set_password(obj['password'])
	user.is_active = True
	user.key_activation = None
	user.save()
	return True

'''
* identification
* balance_contributions
* total_quota
* contributions
* utilized_quota
'''
@transaction.atomic
def bulk_update_users(obj):
	for line in obj['file']:
		data = line.decode('utf-8').strip().split("\t")
		info = {}
		identification = int(data[0])
		info['balance_contributions']=int(round(float(data[1]),0))
		info['total_quota']=int(round(float(data[2]),0))
		info['contributions']=int(round(float(data[3]),0))
		info['utilized_quota'] = int(round(float(data[4]),0))
		
		success, state = update_user_finance(None,identification,info)
		if not success:
			logger.error('User with identification: {}, not exists'.format(identification))
			continue

def get_profile_attr(profiles, attr):
	users = UserProfile.objects.filter(role__in = profiles)
	list_attr = []
	for user in users:
		list_attr.append(getattr(user, attr))
	return list_attr