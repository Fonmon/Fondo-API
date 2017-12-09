from .models import UserAuth
from django.contrib.auth.hashers import check_password

class CustomBackend(object):

	def authenticate(self,username=None, password=None):
		try:
			user = UserAuth.objects.get(email = username)
			pwd_valid = check_password(username+password,user.password)
			if pwd_valid:
				return user
			return None
		except UserAuth.DoesNotExist:
			return None

	def get_user(self,email):
		try:
			return UserAuth.objects.get(email=email)
		except UserAuth.DoesNotExist:
			return None