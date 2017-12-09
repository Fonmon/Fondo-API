from rest_framework import serializers
from .models import User,UserAuth,UserFinance,Loan

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('full_name', 'identification')

class UserAuthSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserAuth
		fields = ('email','role','active','user_id')

class UserFinance(serializers.ModelSerializer):
	class Meta:
		model = UserFinance
		fields = ('contributions','balance_contributions',
			'total_quota','available_quota','user_id')

class Loan(serializers.ModelSerializer):
	class Meta:
		model = Loan
		fields = ('value','timelimit','disbursement_date',
			'created_at','fee','state','user_id')
