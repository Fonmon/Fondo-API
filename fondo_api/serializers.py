from rest_framework import serializers
from .models import UserProfile,UserFinance,Loan,LoanDetail,ActivityYear,Activity

dateFormat = "%d %b. %Y"

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
	disbursement_date = serializers.DateField(format=dateFormat)
	# created_at = serializers.DateTimeField(format=dateFormat)
	class Meta:
		model = Loan
		fields = ('value','timelimit','disbursement_date', 'payment',
			'created_at','fee','comments','state','user_full_name','id','rate')

	def get_user_full_name(self, obj):
		return '{} {}'.format(obj.user.first_name, obj.user.last_name)

	def get_created_at(self, obj):
		return obj.created_at.strftime(dateFormat)

class LoanDetailSerializer(serializers.ModelSerializer):
	payday_limit = serializers.DateField(format=dateFormat)
	from_date = serializers.DateField(format=dateFormat)
	class Meta:
		model = LoanDetail
		fields = ('minimum_payment', 'total_payment','payday_limit','interests',
			'capital_balance','from_date')

class ActivityYearSerializer(serializers.ModelSerializer):
	class Meta:
		model = ActivityYear
		fields = ('id','year')

class ActivityGeneralSerializer(serializers.ModelSerializer):
	class Meta:
		model = Activity
		fields = ('id','name')