from rest_framework import serializers
from .models import UserProfile,UserFinance,Loan,LoanDetail

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
			'total_quota','available_quota','user_id')

class LoanSerializer(serializers.ModelSerializer):
	user_full_name = serializers.SerializerMethodField()
	created_at = serializers.SerializerMethodField()
	#state = serializers.CharField(source='get_state_display')
	#fee = serializers.CharField(source='get_fee_display')
	class Meta:
		model = Loan
		fields = ('value','timelimit','disbursement_date', 'payment',
			'created_at','fee','comments','state','user_full_name','id','rate')

	def get_user_full_name(self, obj):
		return '{} {}'.format(obj.user.first_name, obj.user.last_name)

	def get_created_at(self,obj):
		date = obj.created_at
		return '{}-{}-{}'.format(date.year,date.month,date.day)

class LoanDetailSerializer(serializers.ModelSerializer):
	class Meta:
		model = LoanDetail
		fields = ('current_balance','interest','last_payment_date', 'total_payment',
			'last_payment_value','payday_limit')