from rest_framework import serializers
from babel.dates import format_date
from django.conf import settings
from django.utils import timezone

from fondo_api.models import *

class UserProfileSerializer(serializers.ModelSerializer):
	full_name = serializers.SerializerMethodField()
	role_display = serializers.CharField(source='get_role_display')

	class Meta:
		model = UserProfile
		fields = ('full_name', 'identification','email','role_display','id',
				  'first_name', 'last_name', 'role', 'birthdate')

	def get_full_name(self, obj):
		return '{} {}'.format(obj.first_name, obj.last_name)

class UserFinanceSerializer(serializers.ModelSerializer):
	last_modified = serializers.SerializerMethodField()
	total_savingaccounts = serializers.SerializerMethodField()

	class Meta:
		model = UserFinance
		fields = ('contributions','balance_contributions','total_quota','available_quota',
				  'last_modified','utilized_quota','total_savingaccounts')

	def get_last_modified(self, obj):
		return format_date(obj.last_modified,locale=settings.LANGUAGE_LOCALE)

	def get_total_savingaccounts(self, obj):
		accounts = SavingAccount.objects.filter(user_id=obj.user.id, state=0)
		values = [acc.value for acc in accounts]
		return sum(values)


class UserPreferenceSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserPreference
		fields = ('notifications', 'primary_color', 'secondary_color')

class UserFullInfoSerializer(serializers.Serializer):
	user = serializers.SerializerMethodField()
	finance = serializers.SerializerMethodField()
	preferences = serializers.SerializerMethodField()

	class Meta:
		fields = ('user', 'finance')

	def get_user(self, obj):
		serializer = UserProfileSerializer(obj["finance"].user)
		return serializer.data

	def get_finance(self, obj):
		serializer = UserFinanceSerializer(obj["finance"])
		return serializer.data

	def get_preferences(self, obj):
		serializer = UserPreferenceSerializer(obj["preference"])
		return serializer.data

class UserBirthdateSerializer(serializers.ModelSerializer):
	full_name = serializers.SerializerMethodField()

	class Meta:
		model = UserProfile
		fields = ('birthdate', 'full_name')

	def get_full_name(self, obj):
		return '{} {}'.format(obj.first_name, obj.last_name)

class LoanSerializer(serializers.ModelSerializer):
	user_full_name = serializers.SerializerMethodField()
	created_at = serializers.SerializerMethodField()
	disbursement_date = serializers.SerializerMethodField()
	is_refinanced = serializers.SerializerMethodField()

	class Meta:
		model = Loan
		fields = ('value','timelimit','disbursement_date', 'payment',
			'created_at','fee','comments','state','user_full_name','id','rate',
			'is_refinanced', 'refinanced_loan', 'user_id', 'disbursement_value')

	def get_user_full_name(self, obj):
		return '{} {}'.format(obj.user.first_name, obj.user.last_name)

	def get_created_at(self, obj):
		created_at = timezone.localtime(obj.created_at)
		return format_date(created_at,locale=settings.LANGUAGE_LOCALE)
	
	def get_disbursement_date(self, obj):
		return format_date(obj.disbursement_date,locale=settings.LANGUAGE_LOCALE)

	def get_is_refinanced(self, obj):
		return obj.prev_loan != None

class LoanDetailSerializer(serializers.ModelSerializer):
	payday_limit = serializers.SerializerMethodField()
	from_date = serializers.SerializerMethodField()

	class Meta:
		model = LoanDetail
		fields = ('minimum_payment', 'total_payment','payday_limit','interests',
			'capital_balance','from_date')
	
	def get_payday_limit(self, obj):
		return format_date(obj.payday_limit,locale=settings.LANGUAGE_LOCALE)

	def get_from_date(self, obj):
		return format_date(obj.from_date,locale=settings.LANGUAGE_LOCALE)

class ActivityYearSerializer(serializers.ModelSerializer):
	class Meta:
		model = ActivityYear
		fields = ('id', 'year', 'enable')

class ActivityGeneralSerializer(serializers.ModelSerializer):
	class Meta:
		model = Activity
		fields = ('id','name')

class ActivityUserSerializer(serializers.ModelSerializer):
	user = UserProfileSerializer()
	class Meta:
		model = ActivityUser
		fields = ('id','state','user')

class ActivityDetailSerializer(serializers.ModelSerializer):
	users = serializers.SerializerMethodField()

	class Meta:
		model = Activity
		fields = ('id','name','date','value','users')

	def get_users(self, obj):
		serializer = ActivityUserSerializer(obj.activityuser_set.order_by('user_id'), many=True)
		return serializer.data

class FileSerializer(serializers.ModelSerializer):
	type_display = serializers.CharField(source='get_type_display')

	class Meta:
		model = File
		fields = ('id', 'display_name', 'type_display')

class PowerSerializer(serializers.ModelSerializer):
	requestee = serializers.SerializerMethodField()
	requester = serializers.SerializerMethodField()

	class Meta:
		model = Power
		fields = ('id', 'state', 'meeting_date', 'requestee', 'requester')

	def get_requestee(self, obj):
		return "{} {}".format(obj.requestee.first_name, obj.requestee.last_name)

	def get_requester(self, obj):
		return "{} {}".format(obj.requester.first_name, obj.requester.last_name)

class SavingAccountSerializer(serializers.ModelSerializer):
	user_full_name = serializers.SerializerMethodField()
	created_at = serializers.SerializerMethodField()
	end_date = serializers.SerializerMethodField()

	class Meta:
		model = SavingAccount
		fields = ('value','created_at','state','user_full_name',
		  'id','end_date',)

	def get_user_full_name(self, obj):
		return '{} {}'.format(obj.user.first_name, obj.user.last_name)

	def get_created_at(self, obj):
		created_at = timezone.localtime(obj.created_at)
		return format_date(created_at, locale=settings.LANGUAGE_LOCALE)

	def get_end_date(self, obj):
		return format_date(obj.end_date, locale=settings.LANGUAGE_LOCALE)