import logging
from django.db import IntegrityError,transaction
from django.core.paginator import Paginator
from django.conf import settings
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from babel.dates import format_date
from babel.numbers import decimal, format_decimal, format_number
from datetime import datetime

from fondo_api.models import UserProfile, UserFinance, Loan, LoanDetail, SchedulerTask
from fondo_api.serializers import LoanSerializer,LoanDetailSerializer
from fondo_api.logic.sender_mails import *
from fondo_api.logic.notifications_logic import send_notification
from fondo_api.logic.user_logic import get_profile_attr
from fondo_api.logic.date_utils import days360

LOANS_PER_PAGE = 10
logger = logging.getLogger(__name__)

def create_loan(user_id, obj, refinance = False, prev_loan = None):
	user_finance = UserFinance.objects.get(user_id = user_id)
	if obj['value'] > user_finance.available_quota and not refinance:
		return (False, 'User does not have available quota')
	user = user_finance.user
	# Calculate rate with timelimit
	rate = 0.02
	if 6 < obj['timelimit'] and obj['timelimit'] <= 12:
		rate = 0.025
	elif 12 < obj['timelimit'] and obj['timelimit'] <= 24:
		rate = 0.03
	elif obj['timelimit'] > 24:
		rate = 0.03
		obj['timelimit'] = 24

	newLoan = Loan.objects.create(
		value = obj['value'],
		timelimit = obj['timelimit'],
		disbursement_date = obj['disbursement_date'],
		fee = obj['fee'],
		payment = obj['payment'],
		comments = obj['comments'],
		rate = rate,
		user = user,
		prev_loan = prev_loan,
		disbursement_value = obj['disbursement_value']
	)

	# send notification
	send_notification(get_profile_attr([0,2], 'id'), "Ha sido creada una nueva solicitud de crédito", "/loan/{}".format(newLoan.id))
	return (True, newLoan.id)

def get_loans(user_id,page,all_loans=False,state=4, paginate=True):
	if state == 4:
		if not all_loans:
			loans = Loan.objects.filter(user_id=user_id).order_by('-created_at','-id')
		else:
			loans = Loan.objects.all().order_by('-created_at','-id')
	else:
		if not all_loans:
			loans = Loan.objects.filter(user_id=user_id,state=state).order_by('-created_at','-id')
		else:
			loans = Loan.objects.filter(state=state).order_by('-created_at','-id')

	if paginate:
		paginator = Paginator(loans,LOANS_PER_PAGE)
		if page > paginator.num_pages:
			return {'list':[], 'num_pages':paginator.num_pages, 'count': paginator.count}
		page_return = paginator.page(page)
		serializer = LoanSerializer(page_return.object_list,many=True)
		return {'list':serializer.data, 'num_pages':paginator.num_pages, 'count': paginator.count}
	serializer = LoanSerializer(loans,many=True)
	return {'list':serializer.data}

def create_loan_detail(loan,detail):
	loan_detail = LoanDetail.objects.create(
		total_payment=detail['total_payment'],
		minimum_payment=detail['minimum_payment'],
		payday_limit=detail['payday_limit'],
		from_date=loan.disbursement_date,
		interests=detail['interests'],
		capital_balance=loan.value,
		loan=loan
	)
	return loan_detail

def update_loan(id,state):
	with transaction.atomic():
		try:
			loan = Loan.objects.get(id = id)
		except Loan.DoesNotExist:
			return (False,'Loan does not exist')
		loan.state = state
		loan.save()
		if state == 1:
			table, detail = generate_table(loan)
			if loan.prev_loan is not None:
				loan.prev_loan.state = 3
				loan.prev_loan.save()
			loan_detail = create_loan_detail(loan, detail)
			send_change_state_loan(loan,'approved',table)
			return (True,LoanDetailSerializer(loan_detail).data)
		if state == 2:
			send_change_state_loan(loan,'denied')
			if loan.prev_loan is not None:
				loan.prev_loan.refinanced_loan = None
				loan.prev_loan.save()
		if state == 3:
			remove_scheduled_tasks(id)
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
	first_payment_value = 0
	payday_limit = None
	total_payment = 0
	first_interests = 0
	for i in range(1,fee+1):
		payment_date = initial_date + (relativedelta(months=+i) if loan.fee == 0 else relativedelta(months=+loan.timelimit))
		interests = calculate_interests(loan,initial_balance,payment_date,initial_date_display)
		payment_value = constant_payment + interests
		final_balance = initial_balance - constant_payment
		if i == 1:
			first_payment_value = int(round(payment_value,0))
			first_interests = int(round(interests,0))
			payday_limit = payment_date
		total_payment += payment_value
		with decimal.localcontext(decimal.Context(rounding=decimal.ROUND_HALF_DOWN)):
			table += '<tr>'
			table += '<td>{}</td>'.format(i)
			table += '<td>${}</td>'.format(format_number(format_decimal(round(initial_balance,2),format='#'),locale=settings.LANGUAGE_LOCALE))
			table += '<td>{}</td>'.format(format_date(initial_date_display,locale=settings.LANGUAGE_LOCALE))
			table += '<td>${}</td>'.format(format_number(format_decimal(round(interests,2),format='#'),locale=settings.LANGUAGE_LOCALE))
			table += '<td>${}</td>'.format(format_number(format_decimal(round(constant_payment,2),format='#'),locale=settings.LANGUAGE_LOCALE))
			table += '<td>{}</td>'.format(format_date(payment_date,locale=settings.LANGUAGE_LOCALE))
			table += '<td>${}</td>'.format(format_number(format_decimal(round(payment_value,2),format='#'),locale=settings.LANGUAGE_LOCALE))
			table += '<td>${}</td>'.format(format_number(format_decimal(round(final_balance,2),format='#'),locale=settings.LANGUAGE_LOCALE))
			table += '</tr>'
		initial_balance = final_balance
		initial_date_display = payment_date
	table += '</table>'
	return (table,{
		'payday_limit':payday_limit,
		'minimum_payment':first_payment_value,
		'total_payment':int(round(total_payment,0)),
		'interests':first_interests
	})

def calculate_interests(loan,initial_balance,payment_date,initial_date_display):
	# diff_dates = relativedelta(payment_date, initial_date_display)
	# diff_days = (diff_dates.years*12*30) + (diff_dates.months*30) + diff_dates.days
	diff_days = days360(initial_date_display, payment_date)
	interests = ((initial_balance*loan.rate)/30)*diff_days
	return interests

def payment_projection(loan_id, to_date):
	try:
		loan_detail = LoanDetail.objects.get(loan_id=loan_id)
		loan = loan_detail.loan
		interests = calculate_interests(loan,loan_detail.capital_balance,to_date,loan_detail.from_date)
		return {
			'interests': int(round(interests,0)),
			'capital_balance': loan_detail.capital_balance
		}
	except LoanDetail.DoesNotExist:
		return None

def refinance_loan(loan_id, new_loan, user_id):
	try:
		loan = Loan.objects.get(id=loan_id)
		if loan.state != 1 or user_id != loan.user.id:
			return None
		to_date = datetime.strptime(new_loan['disbursement_date'],'%Y-%m-%d').date()
		payment = payment_projection(loan_id, to_date)
		new_loan['value'] = payment['capital_balance']
		comment = 'Refinanciación del crédito #{}, cuyo valor'.format(loan_id)
		if new_loan['includeInterests']:
			new_loan['value'] += payment['interests']
			comment = '{} incluye intereses'.format(comment)
		else:
			comment = '{} no incluye intereses'.format(comment)
		new_loan['comments'] = '{}. {}'.format(comment, new_loan['comments'])
		new_loan['payment'] = 2
		new_loan['disbursement_value'] = None

		state, new_loan_id = create_loan(user_id, new_loan, True, loan)
		loan.refinanced_loan = new_loan_id
		loan.save()
		return new_loan_id
	except Loan.DoesNotExist:
		return None

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

def update_loan_detail(obj):
	try:
		loan_detail = LoanDetail.objects.get(loan_id = obj['id'])
	except LoanDetail.DoesNotExist:
		raise
	loan_detail.total_payment = obj['total_payment']
	loan_detail.minimum_payment = obj['minimum_payment']
	loan_detail.payday_limit = obj['payday_limit']
	loan_detail.interests = obj['interests']
	loan_detail.capital_balance = obj['capital_balance']
	loan_detail.from_date = obj['from_date']
	loan_detail.save()
	create_scheduled_task(obj['payday_limit'], loan_detail.loan_id)

def create_scheduled_task(payday_limit, loan_id):
	tasks = SchedulerTask.objects.filter(payload__loan_id = loan_id, processed = False)
	if len(tasks) != 0:
		return

	payday_limit = datetime.strptime(payday_limit, '%Y-%m-%d').date()
	five_days_date = payday_limit - relativedelta(days=5)
	five_days_date = datetime(five_days_date.year, five_days_date.month, five_days_date.day)
	before_date = payday_limit - relativedelta(days=1)
	before_date = datetime(before_date.year, before_date.month, before_date.day)
	message = "Recuerde que la fecha límite de pago para el crédito {}, es el: {}"
	payload = {}
	payload["loan_id"] = loan_id
	payload["message"] = message.format(loan_id, format_date(payday_limit, locale=settings.LANGUAGE_LOCALE))

	SchedulerTask.objects.create(
		type = 0,
		run_date = five_days_date,
		payload = payload
	)
	SchedulerTask.objects.create(
		type = 0,
		run_date = before_date,
		payload = payload
	)

def remove_scheduled_tasks(loan_id):
	SchedulerTask.objects.filter(payload__loan_id = loan_id).delete()

'''
TODO: improve creating a map with keys and indexes
* Loan ID
* Total payment
* Minimum payment
* Payday limit
* Interests
* Capital balance
* From date
'''
@transaction.atomic
def bulk_update_loans(obj):
	loan_ids = []
	for line in obj['file']:
		data = line.decode('utf-8').strip().split("\t")
		info = {}
		loan_id = int(data[0])
		loan_ids.append(loan_id)
		info['id'] = loan_id
		info['total_payment']=int(round(float(data[1]),0))
		info['minimum_payment']=int(round(float(data[2]),0))
		date = data[3].strip().split("/")
		info['payday_limit']="{}-{}-{}".format(date[2],date[1],date[0])
		info['interests'] = int(round(float(data[4]),0))
		info['capital_balance'] = int(round(float(data[5]),0))
		date = data[6].strip().split("/")
		info['from_date']="{}-{}-{}".format(date[2],date[1],date[0])
		try:
			update_loan_detail(info)
		except LoanDetail.DoesNotExist:
			logger.error('Loan with id: {}, not exists'.format(loan_id))
			continue
	# auto closing loans
	loans = get_loans(None,None,True,1,False)['list']
	for loan in loans:
		loan_id = loan['id']
		if loan_id not in loan_ids:
			logger.info('Auto closing loan with id {}'.format(loan_id))
			update_loan(loan_id,3)