"""
Django settings for development environment
"""

from .base import *

ENVIRONMENT = 'test'

SECRET_KEY = 'test'

ALLOWED_HOSTS = []

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True