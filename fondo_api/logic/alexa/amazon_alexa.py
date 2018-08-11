import os, re, base64, hashlib, json
import urllib.request, logging
from datetime import datetime
from OpenSSL import crypto
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15, PSS, OAEP
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.exceptions import InvalidSignature

logger = logging.getLogger(__name__)

class AmazonAlexa:
    REQUEST_TYPES = [
        "LaunchRequest",
        "IntentRequest",
        "SessionEndedRequest"
    ]

    SIGNATURE_ALGORITHM = "SHA1withRSAencryption"
    CHARACTER_ENCODING = "UTF-8"
    SIGNATURE_CERTIFICATE_TYPE = "X.509"
    SIGNATURE_TYPE = "RSA"
    ECHO_API_DOMAIN_NAME = "echo-api.amazon.com"

    HEADER_SIGNATURE_URL = "HTTP_SIGNATURECERTCHAINURL"
    HEDAER_SIGNATURE = "HTTP_SIGNATURE"

    def __init__(self):
        # TODO: verify that objects are not remove and created for each request
        self.certificate_cache = None

    def verify_authenticity(self):
        try:
            self.verify_request_obj()
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
        url = self.request.META.get(AmazonAlexa.HEADER_SIGNATURE_URL, None)
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
                stream = urllib.request.urlopen(self.request.META.get(AmazonAlexa.HEADER_SIGNATURE_URL))
                self.certificate_cache = stream.read()
            # cert_x509=x509.load_pem_x509_certificate(self.certificate_cache, default_backend())
            cert_x509 = crypto.load_certificate(crypto.FILETYPE_PEM, self.certificate_cache)
            # if not cert_x509.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == 'echo-api.amazon.com':
            # if cert_x509.get_subject().CN != 'echo-api.amazon.com':
            #     raise Exception(400, "The domain is not correct")
            # if cert_x509.has_expired():
            #     raise Exception(400, "The certificate has expired")

            # public_key = cert_x509.public_key()
            # body = str(self.data).encode(encoding=AmazonAlexa.CHARACTER_ENCODING)
            decoded_signature = base64.b64decode(self.request.META.get(AmazonAlexa.HEDAER_SIGNATURE))
            
            # public_key.verify(decoded_signature, self.body, PKCS1v15(), SHA1())
            ret = crypto.verify(cert_x509, decoded_signature, self.body, "sha1")
            # print(ret)
        except Exception as exception:
            print(exception)
            logger.error('Error verifying signature')
            raise Exception(500, "Internal error")

    def process(self):
        if not (hasattr(self,'request') or hasattr(self,'data') or hasattr(self, 'body')):
            return False
        try:
            self.verify_authenticity()
        except:
            raise
        else:
            return True

    def set_request(self, request):
        self.request = request
        self.body = request.body
        self.data = request.data