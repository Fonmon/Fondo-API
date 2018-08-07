import os, re
from datetime import datetime

class AmazonAlexa:
    REQUEST_TYPES = [
        "LaunchRequest",
        "IntentRequest",
        "SessionEndedRequest"
    ]

    SIGNATURE_ALGORITHM = "SHA1withRSA"
    CHARACTER_ENCODING = "UTF-8"
    SIGNATURE_CERTIFICATE_TYPE = "X.509"
    SIGNATURE_TYPE = "RSA"
    ECHO_API_DOMAIN_NAME = "echo-api.amazon.com"

    def __init__(self):
        self.certificate_cache = None # TODO: add certificate to cache

    def verify_authenticity(self):
        try:
            self.verify_request_obj()
            self.verify_timestamp()
            self.verify_signature_cert_url()
            self.verify_signature()
        except:
            raise
        else:
            skill_id = os.environ.get('AWS_SKILL_ID')
            if not skill_id == self.data['session']['application']['applicationId']:
                raise Exception(403, 'The provided Skill ID is not correct')

    def verify_request_obj(self):
        if 'session' not in self.data or \
           'application' not in self.data['session'] or \
           'applicationId' not in self.data['session']['application'] or \
           'request' not in self.data or \
           'type' not in self.data['request'] or \
           'timestamp' not in self.data['request']:
           raise Exception(422, 'Request object is bad formed')

    def verify_timestamp(self):
        request_date = datetime.strptime(self.data['request']['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
        now = datetime.now()
        seconds = (now - request_date).total_seconds()
        if seconds > 150:
            raise Exception(400, 'Timestamp has exceed the limit of 150 seconds')

    def verify_signature_cert_url(self):
        url = self.request.META.get('HTTP_SIGNATURECERTCHAINURL', None)
        regex = re.compile(
            r'^https://'
            r's3.amazonaws.com'
            r'(:443)?'
            r'/echo.api'
            r'/[a-zA-Z0-9./-]+.pem'
        )
        if url is None or re.match(regex, url) is None:
            raise Exception(400, 'Header SignatureCertChainUrl is not as expected')

    def verify_signature(self):
        pass

    def process(self):
        if not (hasattr(self,'request') or hasattr(self,'data')):
            return False
        try:
            self.verify_authenticity()
        except:
            raise
        else:
            return True

    def set_request(self, request):
        self.request = request
        self.data = request.data