import json
from django.urls import reverse
from django.test.client import encode_multipart, BOUNDARY, MULTIPART_CONTENT
from mock import patch, MagicMock
from rest_framework import status
from google.cloud.storage import Client

from fondo_api.tests.abstract_test import AbstractTest
from fondo_api.models import *

view_file = 'view_file'
view_file_detail = 'view_file_detail'

class FileViewTest(AbstractTest):
  def setUp(self):
    self.create_user()
    self.token = self.get_token('mail_for_tests@mail.com','password')

  def test_post_file_bad_request(self):
    response = self.client.post(
			reverse(view_file),
			data = json.dumps({
        'name': 'New file',
        'type': 'proceeding'
      }),
			content_type='application/json',
			**self.get_auth_header(self.token)
		)
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

  @patch.object(Client, 'get_bucket')
  def test_post_file_exception(self, bucket):
    blob = MagicMock()
    blob.exists.return_value = False
    blob.upload_from_file.side_effect = Exception('error uploading file')
    bucket.return_value.blob.return_value = blob
    response = self.client.post(
      reverse(view_file),
      data=encode_multipart('file', {
        'name': 'New file',
        'file': MagicMock(),
        'type': 0
      }),
			content_type='multipart/form-data; boundary=file',
			**self.get_auth_header(self.token)
		)
    self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)