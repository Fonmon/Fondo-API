from ..models import UserProfile,UserFinance,Loan,LoanDetail
from django.db import IntegrityError,transaction
from django.core.paginator import Paginator
from ..serializers import LoanSerializer,LoanDetailSerializer
from dateutil.relativedelta import relativedelta
from .sender_mails import *
from decimal import Decimal
import locale

LOANS_PER_PAGE = 10
locale.setlocale(locale.LC_ALL, '')

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
	newLoan = Loan.objects.create(
		value = obj['value'],
		timelimit = obj['timelimit'],
		disbursement_date = obj['disbursement_date'],
		fee = obj['fee'],
		payment = obj['payment'],
		comments = obj['comments'],
		rate = rate,
		user = user
	)
	return (True, newLoan.id)

# TODO: add filter by state
def get_loans(user_id,page,all_loans=False):
	if not all_loans:
		loans = Loan.objects.filter(user_id=user_id).order_by('-created_at')
	else:
		loans = Loan.objects.all().order_by('-created_at')

	paginator = Paginator(loans,LOANS_PER_PAGE)
	if page > paginator.num_pages:
		return {'list':[], 'num_pages':paginator.num_pages}
	page_return = paginator.page(page)
	serializer = LoanSerializer(page_return.object_list,many=True)
	return {'list':serializer.data, 'num_pages':paginator.num_pages}

def create_loan_detail(loan,detail):
	try:
		loan_detail = LoanDetail.objects.create(
			current_balance=loan.value,
			interest=detail['interest'],
			total_payment=detail['total_payment'],
			payday_limit=detail['payday_limit'],
			loan=loan
		)
	except IntegrityError:
		raise
	return loan_detail

def update_loan(id,state):
	with transaction.atomic():
		try:
			loan = Loan.objects.get(id = id)
			user_finance = UserFinance.objects.get(user_id = loan.user.id)
		except Loan.DoesNotExist:
			return (False,'Loan does not exist')
		loan.state = state
		loan.save()
		if state == 1:
			table, detail = generate_table(loan)
			loan_detail = create_loan_detail(loan, detail)
			user_finance.available_quota -= loan.value
			user_finance.save()
			send_approved_loan(loan,table)
			return (True,LoanDetailSerializer(loan_detail).data)
		elif state == 3:
			user_finance.available_quota += loan.value
			user_finance.save()
	return (True,'')

def generate_table(loan):
	table = '<table style="width:100%" border="1">'
	table += ('<tr>'
		'<th>Cuota</th>'
		'<th>Saldo inicial</th>'
		'<th>Fecha inicial</th>'
		'<th>Intereses</th>'
		'<th>Abono a capital</th>'
		'<th>Fecha de pago</th>'
		'<th>Valor pago</th>'
		'<th>Saldo final</th>'
	'</tr>')
	fee = 1
	if loan.fee == 0:
		fee = loan.timelimit
	initial_date = loan.disbursement_date
	initial_date_display = initial_date
	initial_balance = Decimal(loan.value)
	constant_payment = Decimal(loan.value)/fee

	#info to store
	first_interest = 0
	payday_limit = None
	total_payment = 0
	for i in range(1,fee+1):
		payment_date = initial_date + relativedelta(months=+i) if loan.fee == 0 else initial_date + relativedelta(months=+loan.timelimit)
		diff_dates = relativedelta(payment_date, initial_date_display)
		if diff_dates.months == 0 and diff_dates.years > 0:
			diff_dates.months = diff_dates.years*12
		interests = ((initial_balance*loan.rate)/30)*(diff_dates.months*30)
		payment_value = constant_payment + interests
		final_balance = initial_balance - constant_payment
		if i == 1:
			first_interest = int(round(interests,0))
			payday_limit = payment_date
		total_payment += payment_value
		table += '<tr>'
		table += '<td>{}</td>'.format(i)
		table += '<td>${}</td>'.format(locale.format('%d',round(initial_balance,2),True))
		table += '<td>{}</td>'.format(initial_date_display)
		table += '<td>${}</td>'.format(locale.format('%d',round(interests,2),True))
		table += '<td>${}</td>'.format(locale.format('%d',round(constant_payment,2),True))
		table += '<td>{}</td>'.format(payment_date)
		table += '<td>${}</td>'.format(locale.format('%d',round(payment_value,2),True))
		table += '<td>${}</td>'.format(locale.format('%d',round(final_balance,2),True))
		table += '</tr>'
		initial_balance = final_balance
		initial_date_display = payment_date
	table += '</table>'
	return (table,{
		'interest':first_interest,
		'payday_limit':payday_limit,
		'total_payment':int(round(total_payment,0))
	})

def get_loan(id):
	try:
		loan = Loan.objects.get(id = id)
	except Loan.DoesNotExist:
		return (False,'')
	serializer = LoanSerializer(loan)
	if loan.state == 1:
		loan_detail = LoanDetail.objects.get(loan_id=id)
		serializer_detail = LoanDetailSerializer(loan_detail)
		return (True,{
			'loan':serializer.data,
			'loan_detail':serializer_detail.data
		})
	return (True,{
		'loan':serializer.data
	})