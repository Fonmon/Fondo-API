from django.core.mail import send_mail
from django.template.loader import render_to_string
import os

def send_activation_mail(user):
	params = { 
		'user_full_name': '{} {}'.format(user.first_name,user.last_name),
		'user_id': user.id,
		'user_key': user.key_activation,
		'host_url': os.environ.get('HOST_URL_APP')
	}
	html_template = render_to_string('activation/activation_email.html',params)
	subject = render_to_string('activation/activation_subject.txt')
	from_email = os.environ.get('EMAIL_HOST_USER')
	to = user.email
	value = send_mail(
		subject,
		'',
		from_email,
		[to],
		html_message=html_template,
		fail_silently=False
	)
	return value == 1

def send_approved_loan(loan,loan_table):
	params = {
		'loan_id':loan.id,
		'loan_table':loan_table
	}
	html_template = render_to_string('loans/approved_email.html',params)
	subject = render_to_string('loans/approved_subject.txt')
	from_email = os.environ.get('EMAIL_HOST_USER')
	to = loan.user.email
	value = send_mail(
		subject,
		'',
		from_email,
		[to],
		html_message=html_template,
		fail_silently=False
	)
	return value == 1