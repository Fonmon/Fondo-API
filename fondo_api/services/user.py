import binascii
import os
import logging
from django.contrib.auth.models import User
from django.db import IntegrityError,transaction
from django.core.paginator import Paginator
from django.conf import settings
from rest_framework.authtoken.models import Token 
from babel.dates import format_date
from datetime import datetime

from fondo_api.models import UserProfile,UserFinance,UserPreference, Power
from fondo_api.serializers import UserProfileSerializer, UserFullInfoSerializer, UserBirthdateSerializer,\
  PowerSerializer
from fondo_api.enums import EmailTemplate

class UserService:

	def __init__(self, notification_service = None, mail_service = None):
		self.ITEMS_PER_PAGE = 10
		self.__logger = logging.getLogger(__name__)
		self.__notification_service = notification_service
		self.__mail_service = mail_service

	def create_user(self, obj):
		try:
			with transaction.atomic():
				user = UserProfile.objects.create_user(
					identification = obj['identification'],
					role = obj['role'],
					first_name = obj['first_name'],
					last_name = obj['last_name'],
					email = obj['email'],
					username = obj['email'],
					key_activation = self.__generate_key(),
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
				UserPreference.objects.create(user=user)
				mail_params = {
					'user_full_name': '{} {}'.format(user.first_name, user.last_name),
					'user_id': user.id,
					'user_key': user.key_activation,
					'host_url': os.environ.get('HOST_URL_APP')
				}
				if not self.__mail_service.send_mail(EmailTemplate.USER_ACTIVATION, [user.email], mail_params):
					transaction.set_rollback(True)
					return (False, 'Invalid email');
		except IntegrityError as error:
			return (False, 'Identification/email already exists')
		return (True, 'Success')

	def get_users(self, page):
		users = UserProfile.objects.filter(is_active=True).order_by('id')
		if page is not None:
			paginator = Paginator(users, self.ITEMS_PER_PAGE)
			if page > paginator.num_pages:
				return {'list': [], 'num_pages': paginator.num_pages, 'count': paginator.count}
			page_return = paginator.page(page)
			serializer = UserProfileSerializer(page_return.object_list, many=True)
			return {'list': serializer.data, 'num_pages': paginator.num_pages, 'count': paginator.count}
		serializer = UserProfileSerializer(users, many=True)
		return {'list': serializer.data}

	def get_user(self, id):
		try:
			user_finance = UserFinance.objects.get(user_id=id)
			user_preference = UserPreference.objects.get(user_id=id)
		except:
			return (False, {})
		serializer = UserFullInfoSerializer({
			'finance': user_finance,
			'preference': user_preference
		})
		return (True, serializer.data)

	def get_user_by_email(self, email):
		try:
			user = User.objects.get(email=email)
			return user
		except:
			return None

	def inactive_user(self, id):
		try:
			user = User.objects.get(id=id)
		except User.DoesNotExist:
			return False
		user.is_active = False
		user.save()
		return True

	def update_user(self, id, obj):
		if obj['type'] == 'personal':
			return self.__update_user_personal(id, obj['personal'])
		if obj['type'] == 'finance':
			return self.__update_user_finance(id, None, obj['finance'])
		return self.__update_user_preferences(id, obj['preferences'])

	def activate_user(self, id, obj):
		if 'key' not in obj or obj['key'] == '':
			return False
		try:
			user = UserProfile.objects.get(
				id = id,
				key_activation = obj['key'],
				identification = obj['identification']
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
	def bulk_update_users(self, obj):
		for line in obj['file']:
			data = line.decode('utf-8').strip().split("\t")
			info = {}
			identification = int(data[0])
			info['balance_contributions']=int(round(float(data[1]), 0))
			info['total_quota']=int(round(float(data[2]), 0))
			info['contributions']=int(round(float(data[3]), 0))
			info['utilized_quota'] = int(round(float(data[4]), 0))
			
			success, state = self.__update_user_finance(None, identification, info)
			if not success:
				self.__logger.error('User with identification: {}, not exists'.format(identification))
				continue

	def get_users_attr(self, attr, roles=None):
		if roles is not None:
			users = UserProfile.objects.filter(role__in=roles, is_active=True)
		else:
			users = UserProfile.objects.filter(is_active=True)
		list_attr = []
		for user in users:
			list_attr.append(getattr(user, attr))
		return list_attr

	def get_profile(self, user_id):
		return UserProfile.objects.get(id=user_id)

	def get_users_birthdate(self):
		users = UserProfile.objects.filter(is_active=True)
		serializer = UserBirthdateSerializer(users, many=True)
		return serializer.data

	def handle_power_request(self, user_id, request):
		if request['type'].lower() == 'post':
			Power.objects.create(
				meeting_date = request['meeting_date'],
				requester = self.get_profile(user_id),
				requestee = self.get_profile(request['requestee'])
			)
			self.__notification_service.send_notification(
				[request['requestee']], 
				'Te han enviado una solicitud para ser apoderado en una reunion. Revisala',
				'/tool/power'
			)
			return None
		elif request['type'].lower() == 'get':
			objs = []
			page = request['page']
			user = self.get_profile(user_id)
			if request['obj'] == 'requested':
				objs = user.power_requested.all().order_by('-id')
			if request['obj'] == 'requestee':
				objs = user.power_requestee.all().order_by('-id')

			paginator = Paginator(objs, self.ITEMS_PER_PAGE)
			if page > paginator.num_pages:
				return {'list': [], 'num_pages': paginator.num_pages, 'count': paginator.count}
			page_return = paginator.page(page)
			serializer = PowerSerializer(page_return.object_list, many=True)
			return {'list': serializer.data, 'num_pages': paginator.num_pages, 'count': paginator.count}
		elif request['type'].lower() == 'patch':
			power = Power.objects.get(id = request['id'])
			power.state = request['state']
			power.save()
			if power.state == 1:
				mail_params = {
					'requester_full_name': '{} {}'.format(power.requester.first_name, power.requester.last_name),
					'requester_identification': power.requester.identification,
					'requestee_full_name': '{} {}'.format(power.requestee.first_name, power.requestee.last_name),
					'requestee_identification': power.requestee.identification,
					'meeting_date': format_date(power.meeting_date, locale=settings.LANGUAGE_LOCALE),
				}
				self.__mail_service.send_mail(EmailTemplate.POWER_APPROVED, self.get_users_attr('email'), mail_params)
			return None

	def __update_user_preferences(self, id, obj):
		try:
			user_preference = UserPreference.objects.get(user_id = id)
			remove_notifications = user_preference.notifications != obj['notifications']

			user_preference.notifications = obj['notifications']
			user_preference.primary_color = obj['primary_color']
			user_preference.secondary_color = obj['secondary_color']
			user_preference.save()
			if remove_notifications and not user_preference.notifications:
				self.__notification_service.remove_all_subscriptions(id)
		except:
			return (False, 404)
		return (True, 200)

	def __update_user_personal(self, id, obj):
		try:
			with transaction.atomic():
				user = self.get_profile(id)
				user.first_name = obj['first_name']
				user.last_name = obj['last_name']
				user.email = obj['email']
				user.username = obj['email']
				user.identification = obj['identification']
				user.role = obj['role']
				if 'birthdate' in obj:
					user.birthdate = obj['birthdate']
					self.__create_birthdate_notification(user)
				user.save()
		except UserProfile.DoesNotExist:
			return (False, 404)
		except IntegrityError:
			return (False, 409)
		return (True, 200)

	def __update_user_finance(self, id, identification, obj):
		try:
			if id is not None:
				user_finance = UserFinance.objects.get(user_id=id)
			else:
				user_finance = UserFinance.objects.get(user__identification=identification)
		except UserFinance.DoesNotExist:
			return (False, 404)
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
		return (True, 200)

	def __generate_key(self):
		return binascii.hexlify(os.urandom(25)).decode()

	def __create_birthdate_notification(self, user):
		today_year = datetime.now().year
		birthdate = datetime.strptime(user.birthdate, '%Y-%m-%d').date().replace(year=today_year)
		birthdate_time = datetime(birthdate.year, birthdate.month, birthdate.day)
		user_ids = self.get_users_attr("id")
		user_ids.remove(user.id)

		payload = {}
		payload["type"] = "birthdate"
		payload["owner_id"] = user.id
		payload["user_ids"] = user_ids
		payload["target"] = "/"
		payload["message"] = "Hoy está cumpliendo años {} {}".format(user.first_name, user.last_name)

		self.__notification_service.remove_sch_notitfications("birthdate", user.id)
		self.__notification_service.schedule_notification(birthdate_time, payload, 4)