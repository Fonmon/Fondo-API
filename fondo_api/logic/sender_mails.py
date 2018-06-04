from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import os
from . import user_logic

def send_mail(subject,body,recipient_list,bcc_list=[]):
	mail = EmailMessage(
		subject=subject,
		body=body,
		to=recipient_list,
		bcc=bcc_list
	)
	mail.content_subtype = "html"
	return mail.send(fail_silently=False)

def send_activation_mail(user):
	params = { 
		'user_full_name': '{} {}'.format(user.first_name,user.last_name),
		'user_id': user.id,
		'user_key': user.key_activation,
		'host_url': os.environ.get('HOST_URL_APP')
	}
	html_template = render_to_string('activation/activation_email.html',params)
	subject = render_to_string('activation/activation_subject.txt')
	recipient_list = [user.email]
	value = send_mail(
		subject,
		html_template,
		recipient_list
	)
	return value == 1

def send_change_state_loan(loan,state,loan_table=None):
	params = {
		'loan_id':loan.id,
		'loan_table':loan_table
	}
	html_template = render_to_string('loans/{}_email.html'.format(state),params)
	subject = render_to_string('loans/loan_subject.txt')
	bcc_list = user_logic.get_profile_emails([0,2])
	if loan.user.email in bcc_list:
		bcc_list.remove(loan.user.email)
	recipient_list = [loan.user.email]
	
	value = send_mail(
		subject,
		html_template,
		recipient_list,
		bcc_list
	)
	return value == 1