from django import template
import os

register = template.Library()

@register.simple_tag
def host():
    return os.environ.get('HOST_URL_APP')