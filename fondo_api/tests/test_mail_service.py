from mock import patch, MagicMock
from django.test import TestCase

from fondo_api.services.mail import MailService
from fondo_api.enums import EmailTemplate

class MailServiceTest(TestCase):

  @patch('boto3.client')
  def test_send_mail_exception(self, mock):
    SES = MagicMock()
    SES.send_email.side_effect = Exception('there was an error')
    mock.return_value = SES
    
    mail_service = MailService()
    mail_params = {
      'user_full_name': 'Foo Name',
      'user_id': 1,
      'user_key': 'ik3u24kh53kj5hk',
      'host_url': 'http://localhost:3000'
    }
    result = mail_service.send_mail(EmailTemplate.USER_ACTIVATION, ['mail@mail.com'], mail_params)
    self.assertEqual(result, False)

  @patch('boto3.client')
  def test_send_mail_user_activation(self, mock):
    SES = MagicMock()
    SES.send_email.return_value = None
    mock.return_value = SES
    
    mail_service = MailService()
    mail_params = {
      'user_full_name': 'Foo Name',
      'user_id': 1,
      'user_key': 'ik3u24kh53kj5hk',
      'host_url': 'http://localhost:3000'
    }
    result = mail_service.send_mail(EmailTemplate.USER_ACTIVATION, ['mail@mail.com'], mail_params)
    self.assertEqual(result, True)
    SES.send_email.assert_called_once_with(
      Destination={
        'ToAddresses': ['mail@mail.com'],
        'BccAddresses': []
      },
      Message={
        'Body': {
          'Html': {
            'Charset': 'UTF-8',
            'Data': '\nHola Foo Name,\n<br /><br />\nSe te ha creado una cuenta en el Fondo Montañez, para activarla es necesario que entres al siguiente link:<br /><br />\n<a href="http://localhost:3000/activate/1/ik3u24kh53kj5hk">http://localhost:3000/activate/1/ik3u24kh53kj5hk</a>\n<br /><br />\nSi dando clic al link no funciona, por favor copiarlo y pegarlo en una nueva ventana de su navegador.\n<br /><br />\nGracias,<br />\nFondo Montañez<br />\n\n',
          },
        },
        'Subject': {
          'Charset': 'UTF-8',
          'Data': '[Fondo Montañez] Activación de cuenta',
        },
      },
      Source='Fondo Montanez <no-reply@fonmon.minagle.com>',
    )

  @patch('boto3.client')
  def test_send_mail_change_state_loan_approved(self, mock):
    SES = MagicMock()
    SES.send_email.return_value = None
    mock.return_value = SES
    
    mail_service = MailService()
    mail_params = {
      'loan_table': 'some html table',
      'loan_id': 1,
    }
    result = mail_service.send_mail(EmailTemplate.CHANGE_STATE_LOAN_APPROVED, ['mail@mail.com'], mail_params)
    self.assertEqual(result, True)
    SES.send_email.assert_called_once_with(
      Destination={
        'ToAddresses': ['mail@mail.com'],
        'BccAddresses': []
      },
      Message={
        'Body': {
          'Html': {
            'Charset': 'UTF-8',
            'Data': '\nApreciado afiliado,\n<br /><br />\nSe le informa que su solicitud de crédito número: 1, ha sido <strong>APROBADA</strong> por el valor requerido, los cuales serán abonados a la respectiva cuenta.\n<br /><br />\nA continuación, se le envía la proyección de pagos. Por favor, si va a realizar el pago antes de la fecha estipulada, deberá comunicarse con la Tesorería para que le sean re-calculados los intereses.\n<br /><br />\nsome html table\n<br /><br />\nGracias,<br />\nFondo Montañez<br />\n\n',
          },
        },
        'Subject': {
          'Charset': 'UTF-8',
          'Data': '[Fondo Montañez] Solicitud de crédito',
        },
      },
      Source='Fondo Montanez <no-reply@fonmon.minagle.com>',
    )

  @patch('boto3.client')
  def test_send_mail_change_state_loan_denied(self, mock):
    SES = MagicMock()
    SES.send_email.return_value = None
    mock.return_value = SES
    
    mail_service = MailService()
    mail_params = {
      'loan_table': 'some html table',
      'loan_id': 1,
    }
    result = mail_service.send_mail(EmailTemplate.CHANGE_STATE_LOAN_DENIED, ['mail@mail.com'], mail_params)
    self.assertEqual(result, True)
    SES.send_email.assert_called_once_with(
      Destination={
        'ToAddresses': ['mail@mail.com'],
        'BccAddresses': []
      },
      Message={
        'Body': {
          'Html': {
            'Charset': 'UTF-8',
            'Data': '\nApreciado afiliado,\n<br /><br />\nSe le informa que su solicitud de crédito número: 1, ha sido <strong>RECHAZADA</strong>. Favor comuníquese con la tesorería.\n<br /><br />\nGracias,<br />\nFondo Montañez<br />\n\n',
          },
        },
        'Subject': {
          'Charset': 'UTF-8',
          'Data': '[Fondo Montañez] Solicitud de crédito',
        },
      },
      Source='Fondo Montanez <no-reply@fonmon.minagle.com>',
    )

  @patch('boto3.client')
  def test_send_mail_power_approved(self, mock):
    SES = MagicMock()
    SES.send_email.return_value = None
    mock.return_value = SES
    
    mail_service = MailService()
    mail_params = {
      'requester_full_name': 'requester full name',
      'requester_identification': 123,
      'requestee_full_name': 'requestee full name',
      'requestee_identification': 456,
      'meeting_date': '26 sept. 2021',
    }
    result = mail_service.send_mail(EmailTemplate.POWER_APPROVED, ['mail@mail.com'], mail_params)
    self.assertEqual(result, True)
    SES.send_email.assert_called_once_with(
      Destination={
        'ToAddresses': ['mail@mail.com'],
        'BccAddresses': []
      },
      Message={
        'Body': {
          'Html': {
            'Charset': 'UTF-8',
            'Data': '\nSeñores:<br />\nASAMBLEA GENERAL FONDO FAMILIAR<br />\nAtn: Presidente<br />\nBogotá<br /><br />\nYo, requester full name, con número de identificación 123, en mi calidad de afiliado al fondo, manifiesto de manera libre y espontánea que confiero poder amplio y suficiente a requestee full name, con número de identificación 456, para que en mi nombre me represente en la asamblea, convocada para la fecha: 26 sept. 2021, quien participará con voz y voto en todas y cada una de las deliberaciones y decisiones tomadas en la asamblea.<br /><br />\nAtentamente,<br />\nFondo Montañez<br />\n\n',
          },
        },
        'Subject': {
          'Charset': 'UTF-8',
          'Data': '[Fondo Montañez] Poder asamblea',
        },
      },
      Source='Fondo Montanez <no-reply@fonmon.minagle.com>',
    )

  @patch('boto3.client')
  def test_send_mail_repeated_emails(self, mock):
    SES = MagicMock()
    SES.send_email.return_value = None
    mock.return_value = SES
    
    mail_service = MailService()
    mail_params = {
      'loan_table': 'some html table',
      'loan_id': 1,
    }
    result = mail_service.send_mail(EmailTemplate.CHANGE_STATE_LOAN_APPROVED, ['mail@mail.com'], mail_params, ['mail@mail.com', 'mail2@mail.com'])
    self.assertEqual(result, True)
    SES.send_email.assert_called_once_with(
      Destination={
        'ToAddresses': ['mail@mail.com'],
        'BccAddresses': ['mail2@mail.com']
      },
      Message={
        'Body': {
          'Html': {
            'Charset': 'UTF-8',
            'Data': '\nApreciado afiliado,\n<br /><br />\nSe le informa que su solicitud de crédito número: 1, ha sido <strong>APROBADA</strong> por el valor requerido, los cuales serán abonados a la respectiva cuenta.\n<br /><br />\nA continuación, se le envía la proyección de pagos. Por favor, si va a realizar el pago antes de la fecha estipulada, deberá comunicarse con la Tesorería para que le sean re-calculados los intereses.\n<br /><br />\nsome html table\n<br /><br />\nGracias,<br />\nFondo Montañez<br />\n\n',
          },
        },
        'Subject': {
          'Charset': 'UTF-8',
          'Data': '[Fondo Montañez] Solicitud de crédito',
        },
      },
      Source='Fondo Montanez <no-reply@fonmon.minagle.com>',
    )