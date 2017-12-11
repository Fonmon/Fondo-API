from rest_framework import serializers
from .models import UserProfile,UserFinance,Loan

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
	state = serializers.CharField(source='get_state_display')
	fee = serializers.CharField(source='get_fee_display')
	class Meta:
		model = Loan
		fields = ('value','timelimit','disbursement_date',
			'created_at','fee','state','user_full_name','id','rate')

	def get_user_full_name(self, obj):
		return '{} {}'.format(obj.user.first_name, obj.user.last_name)
