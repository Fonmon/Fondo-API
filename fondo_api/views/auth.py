import logging
import os
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.template.response import TemplateResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from fondo_api.services.user import UserService
from fondo_api.services.notification import NotificationService
from fondo_api.services.mail import MailService
from fondo_api.enums import EmailTemplate

notification_service = NotificationService()
mail_service = MailService()
user_service = UserService(notification_service, mail_service)
logger = logging.getLogger(__name__)

class PasswordResetView(auth_views.PasswordResetView):
    def post(self, request):
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            user = user_service.get_user_by_email(data)
            if user != None:
                current_site = get_current_site(request)
                domain = current_site.domain
                params = {
                    'user': user,
                    'protocol': 'https' if settings.ENVIRONMENT == 'production' else 'http',
                    'domain': domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user)
                }
                mail_service.send_mail(EmailTemplate.PASSWORD_RESET, [user.email], params)
        return redirect("/password_reset/done/")

class AuthView(APIView):
    permission_classes = []

    def get(self, request):
        form = AuthenticationForm(request)
        context = {
            'form': form
        }
        return TemplateResponse(request, 'auth/authorize.html', context)

    def post(self, request):
        client_id = request.query_params.get('client_id', '')
        response_type = request.query_params.get('response_type', '')
        redirect_to = request.query_params.get('redirect_uri', '')
        state = request.query_params.get('state', '')

        if client_id != os.environ.get('ALEXA_CLIENT_ID'):
            return Response(status=status.HTTP_400_BAD_REQUEST) 

        request_params = 'client_id={}&response_type={}&redirect_uri={}&state={}'\
            .format(client_id, response_type, redirect_to, state)

        user = authenticate(username=request.POST.get('username', None), password=request.POST.get('password', None))
        if user is None:
            return HttpResponseRedirect('/api/authorize?q=false&{}'.format(request_params))

        token, created = Token.objects.get_or_create(user=user)
        response_params = 'state={}&access_token={}&token_type=Token'.format(state, token.key)
        return HttpResponseRedirect('{}#{}'.format(redirect_to, response_params))