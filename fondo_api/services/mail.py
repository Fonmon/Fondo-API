import os
import boto3
import logging
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from fondo_api.enums import EmailTemplate

class MailService:

	def __init__(self):
		self.CHARSET = "UTF-8"
		self.SOURCE = os.environ['DEFAULT_FROM_EMAIL']

		self.__ses_client = boto3.client('ses',region_name=os.environ['AWS_REGION'])
		self.__logger = logging.getLogger(__name__)

	def send_mail(self, template, recipients, params, bcc=[]):
		try:
			for recipient in recipients:
				if recipient in bcc:
					bcc.remove(recipient)
			
			mail = self.__get_email_from_template(template, params)

			response = self.__ses_client.send_email(
				Destination={
					'ToAddresses': recipients,
					'BccAddresses': bcc
				},
				Message={
					'Body': {
						'Html': {
							'Charset': self.CHARSET,
							'Data': mail['body'],
						},
					},
					'Subject': {
						'Charset': self.CHARSET,
						'Data': mail['subject'],
					},
				},
				Source=self.SOURCE,
    	)
		except Exception as e:
			self.__logger.error('Error sending email: %s', e)
			return False
		else:
			return True

	def __get_email_from_template(self, template, params):
		mail = {
			'body': None,
			'subject': None
		}
		if template == EmailTemplate.USER_ACTIVATION:
			mail['body'] = render_to_string('activation/activation_email.html', params)
			mail['subject'] = render_to_string('activation/activation_subject.txt')
		elif template == EmailTemplate.CHANGE_STATE_LOAN_APPROVED:
			mail['body'] = render_to_string('loans/approved_email.html', params)
			mail['subject'] = render_to_string('loans/loan_subject.txt')
		elif template == EmailTemplate.CHANGE_STATE_LOAN_DENIED:
			mail['body'] = render_to_string('loans/denied_email.html', params)
			mail['subject'] = render_to_string('loans/loan_subject.txt')
		return mail

# def send_mail(subject, body, recipient_list, bcc_list = []):
# 	mail = EmailMessage(
# 		subject = subject,
# 		body = body,
# 		to = recipient_list,
# 		bcc = bcc_list
# 	)
# 	mail.content_subtype = "html"
# 	return mail.send(fail_silently=False)

# def send_activation_mail(user):
# 	params = { 
# 		'user_full_name': '{} {}'.format(user.first_name, user.last_name),
# 		'user_id': user.id,
# 		'user_key': user.key_activation,
# 		'host_url': os.environ.get('HOST_URL_APP')
# 	}
# 	html_template = render_to_string('activation/activation_email.html', params)
# 	subject = render_to_string('activation/activation_subject.txt')
# 	recipient_list = [user.email]
# 	value = send_mail(
# 		subject,
# 		html_template,
# 		recipient_list
# 	)
# 	return value == 1

# def send_change_state_loan(loan, state, loan_table = None, bcc_list = []):
# 	params = {
# 		'loan_id': loan.id,
# 		'loan_table': loan_table
# 	}
# 	html_template = render_to_string('loans/{}_email.html'.format(state), params)
# 	subject = render_to_string('loans/loan_subject.txt')
# 	if loan.user.email in bcc_list:
# 		bcc_list.remove(loan.user.email)
# 	recipient_list = [loan.user.email]
	
# 	value = send_mail(
# 		subject,
# 		html_template,
# 		recipient_list,
# 		bcc_list
# 	)
# 	return value == 1