import os, re, urllib.request, logging, base64
from rest_framework.authtoken.models import Token
from datetime import datetime
from OpenSSL import crypto
from .handlers.launch_handler import LaunchHandler
from .handlers.intent_handler import IntentHandler

logger = logging.getLogger(__name__)

class AmazonAlexa:
    REQUEST_TYPES = [
        "LaunchRequest",
        "IntentRequest",
        "SessionEndedRequest"
    ]

    ECHO_API_DOMAIN_NAME = "echo-api.amazon.com"

    HEADER_SIGNATURE_URL = "HTTP_SIGNATURECERTCHAINURL"
    HEDAER_SIGNATURE = "HTTP_SIGNATURE"

    def __init__(self):
        self.certificate_cache = None

    def verify_authenticity(self):
        try:
            self.verify_request_obj()
            self.verify_token()
            self.verify_timestamp()
            self.verify_signature_cert_url()
            self.verify_signature()
        except:
            self.certificate_cache = None
            raise
        else:
            skill_id = os.environ.get('AWS_SKILL_ID')
            if not skill_id == self.data['session']['application']['applicationId']:
                raise Exception(403, 'The provided Skill ID is not correct')

    def verify_request_obj(self):
        if 'session' not in self.data or \
           'application' not in self.data['session'] or \
           'applicationId' not in self.data['session']['application'] or \
           'user' not in self.data['session'] or \
           'accessToken' not in self.data['session']['user'] or \
           'request' not in self.data or \
           'type' not in self.data['request'] or \
           'timestamp' not in self.data['request']:
           raise Exception(422, 'Request object is bad formed')

    def verify_token(self):
        key = self.data['session']['user']['accessToken']
        try:
            token = Token.objects.get(key = key)
            self.user_id = token.user.id
        except Token.DoesNotExist:
            raise Exception(401, 'Authentication error')

    def verify_timestamp(self):
        request_date = datetime.strptime(self.data['request']['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
        now = datetime.now()
        seconds = (now - request_date).total_seconds()
        if seconds > 150:
            raise Exception(400, 'Timestamp has exceed the limit of 150 seconds')

    def verify_signature_cert_url(self):
        url = self.headers.get(AmazonAlexa.HEADER_SIGNATURE_URL, None)
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
        try:
            if self.certificate_cache is None:
                stream = urllib.request.urlopen(self.headers.get(AmazonAlexa.HEADER_SIGNATURE_URL))
                self.certificate_cache = stream.read()
            cert_x509 = crypto.load_certificate(crypto.FILETYPE_PEM, self.certificate_cache)
        except Exception as exception:
            logger.error('Error loading certificate, exception: %s', exception)
            raise Exception(500, "Internal error loading certificate")
        else:
            if cert_x509.get_subject().CN != AmazonAlexa.ECHO_API_DOMAIN_NAME:
                raise Exception(400, "The domain is not correct")
            if cert_x509.has_expired():
                raise Exception(400, "The certificate has expired")
            try:
                decoded_signature = base64.b64decode(self.headers.get(AmazonAlexa.HEDAER_SIGNATURE))
                crypto.verify(cert_x509, decoded_signature, self.body, 'sha1')
            except Exception as ex:
                logger.error('Error verifying signature, exception: %s', exception)
                raise Exception(500, "Internal error verifying signature")

    def process(self):
        if not (hasattr(self,'headers') or hasattr(self,'data') or hasattr(self, 'body')):
            raise Exception('set_request must be called first')
        try:
            self.verify_authenticity()
            handler = None
            request_type = self.data['request']['type']
            if not request_type in AmazonAlexa.REQUEST_TYPES:
                raise Exception(422, 'Request type is unrecognized')
            
            if request_type == AmazonAlexa.REQUEST_TYPES[0]:
                handler = LaunchHandler(self.data, self.user_id)
            elif request_type == AmazonAlexa.REQUEST_TYPES[1]:
                handler = IntentHandler(self.data, self.user_id)
            else:
                return None
            return handler.handle()
        except Exception as exception:
            raise
        else:
            return True

    def set_request(self, request):
        self.headers = request.META
        self.body = request.body
        self.data = request.data