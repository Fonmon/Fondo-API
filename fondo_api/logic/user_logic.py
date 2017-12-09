from ..models import User,UserAuth
from django.db import IntegrityError

def create_user(obj):
	try:
		user = User.objects.create(
			full_name = obj['full_name'],
			identification = obj['identification']
		)
	except IntegrityError:
		return (False,'Identification already exists')
	try:
		UserAuth.objects.create(
			email = obj['email'],
			role = obj['role'],
			user = user
		)
		#Send email to set password or next login?
		return (True,'Success')
	except IntegrityError:
		return (False,'Email already exists')