from rest_framework import serializers
from .models import UserProfile,UserFinance,Loan,LoanDetail,ActivityYear,Activity, ActivityUser
from babel.dates import format_date
from django.conf import settings

class UserProfileSerializer(serializers.ModelSerializer):
	full_name = serializers.SerializerMethodField()
	role = serializers.CharField(source='get_role_display')
	class Meta:
		model = UserProfile
		fields = ('full_name', 'identification','email','role','id')

	def get_full_name(self, obj):
		return '{} {}'.format(obj.first_name, obj.last_name)

class UserFinanceSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserFinance
		fields = ('contributions','balance_contributions',
			'total_quota','available_quota','user_id','utilized_quota')

class LoanSerializer(serializers.ModelSerializer):
	user_full_name = serializers.SerializerMethodField()
	created_at = serializers.SerializerMethodField()
	disbursement_date = serializers.SerializerMethodField()
	class Meta:
		model = Loan
		fields = ('value','timelimit','disbursement_date', 'payment',
			'created_at','fee','comments','state','user_full_name','id','rate')

	def get_user_full_name(self, obj):
		return '{} {}'.format(obj.user.first_name, obj.user.last_name)

	def get_created_at(self, obj):
		return format_date(obj.created_at,locale=settings.LANGUAGE_LOCALE)
	
	def get_disbursement_date(self, obj):
		return format_date(obj.disbursement_date,locale=settings.LANGUAGE_LOCALE)

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
		fields = ('id','year')

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
