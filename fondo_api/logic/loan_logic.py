from ..models import UserProfile,UserFinance,Loan
from django.db import IntegrityError,transaction
from ..serializers import LoanSerializer

def create_loan(user_id,obj):
	user_finance = UserFinance.objects.get(user_id = user_id)
	if obj['value'] > user_finance.available_quota:
		return (False, 'User does not have available quota')
	user = user_finance.user
	# Calculate rate with timelimit
	rate = 0.02
	if 6 < obj['timelimit'] and obj['timelimit'] <= 12:
		rate = 0.025
	elif 12 < obj['timelimit'] and obj['timelimit'] <= 24:
		rate = 0.03
	Loan.objects.create(
		value = obj['value'],
		timelimit = obj['timelimit'],
		disbursement_date = obj['disbursement_date'],
		fee = obj['fee'],
		rate = rate,
		user = user
	)
	return (True, 'Created')

# TODO: add filter by state
# TODO: pagination
def get_loans(user_id,all_loans=False):
	if not all_loans:
		loans = Loan.objects.filter(user_id=user_id).order_by('-created_at')
	else:
		loans = Loan.objects.all().order_by('-created_at')
	serializer = LoanSerializer(loans,many=True)
	return serializer.data

def update_loan(id,state):
	try:
		loan = Loan.objects.get(id = id)
	except Loan.DoesNotExist:
		return (False,'Loan does not exist')
	loan.state = state
	loan.save()
	return (True,'Success')