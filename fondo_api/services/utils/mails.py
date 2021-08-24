import os
import boto3
from botocore.exceptions import ClientError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

class MailService:

	def send_mail(self):
		try:
			RECIPIENT = "TO_EMAIL"
			params = {
				'loan_id': 1,
				'loan_table': ''
			}
			html_template = render_to_string('loans/{}_email.html'.format('denied'), params)
			subject = render_to_string('loans/loan_subject.txt')
			CHARSET = "UTF-8"

			client = boto3.client('ses',region_name=os.environ['AWS_REGION'])
			response = client.send_email(
        Destination={
            'ToAddresses': [
              RECIPIENT,
            ],
						# 'BccAddresses': []
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': html_template,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': subject,
            },
        },
        Source=os.environ['DEFAULT_FROM_EMAIL'],
    	)
			print(response)
		except ClientError as e:
			print(e.response['Error']['Message'])
		else:
			print("Email sent! Message ID:"),
			print(response['MessageId'])

def send_mail(subject, body, recipient_list, bcc_list = []):
	mail = EmailMessage(
		subject = subject,
		body = body,
		to = recipient_list,
		bcc = bcc_list
	)
	mail.content_subtype = "html"
	return mail.send(fail_silently=False)

def send_activation_mail(user):
	params = { 
		'user_full_name': '{} {}'.format(user.first_name, user.last_name),
		'user_id': user.id,
		'user_key': user.key_activation,
		'host_url': os.environ.get('HOST_URL_APP')
	}
	html_template = render_to_string('activation/activation_email.html', params)
	subject = render_to_string('activation/activation_subject.txt')
	recipient_list = [user.email]
	value = send_mail(
		subject,
		html_template,
		recipient_list
	)
	return value == 1

def send_change_state_loan(loan, state, loan_table = None, bcc_list = []):
	params = {
		'loan_id': loan.id,
		'loan_table': loan_table
	}
	html_template = render_to_string('loans/{}_email.html'.format(state), params)
	subject = render_to_string('loans/loan_subject.txt')
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