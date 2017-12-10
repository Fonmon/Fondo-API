from rest_framework import serializers
from .models import User,UserAuth,UserFinance,Loan

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('full_name', 'identification')

class UserAuthSerializer(serializers.ModelSerializer):
	identification = serializers.CharField(source='user.identification')
	full_name = serializers.CharField(source='user.full_name')
	role = serializers.CharField(source='get_role_display')
	id = serializers.CharField(source='user.id')
	class Meta:
		model = UserAuth
		fields = ('email','role','id','identification','full_name')

class UserFinanceSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserFinance
		fields = ('contributions','balance_contributions',
			'total_quota','available_quota','user_id')

class LoanSerializer(serializers.ModelSerializer):
	user_name = serializers.CharField(source='user.full_name')
	state = serializers.CharField(source='get_state_display')
	fee = serializers.CharField(source='get_fee_display')
	class Meta:
		model = Loan
		fields = ('value','timelimit','disbursement_date',
			'created_at','fee','state','user_name','id','rate')
