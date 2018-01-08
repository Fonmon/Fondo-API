"""
Django settings for production environment
"""

from .base import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = ['api-fonmon.minagle.com','127.0.0.1']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True