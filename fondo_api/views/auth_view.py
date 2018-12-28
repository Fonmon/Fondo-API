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

logger = logging.getLogger(__name__)

class AuthView(APIView):
    permission_classes = []

    def get(self, request):
        form = AuthenticationForm(request)
        context = {
            'form': form
        }
        form.fields['username'].label = "Email"
        return TemplateResponse(request, 'auth/authorize.html', context)

    def post(self,request):
        client_id = request.query_params.get('client_id', '')
        response_type = request.query_params.get('response_type', '')
        redirect_to = request.query_params.get('redirect_uri', '')
        state = request.query_params.get('state', '')

        if client_id != os.environ.get('ALEXA_CLIENT_ID'):
            return Response(status=status.HTTP_400_BAD_REQUEST) 

        request_params = 'client_id={}&response_type={}&redirect_uri={}&state={}'\
            .format(client_id,response_type,redirect_to,state)

        user = authenticate(username=request.POST.get('username', None), password=request.POST.get('password', None))
        if user is None:
            return HttpResponseRedirect('/api/authorize?q=false&{}'.format(request_params))

        token, created = Token.objects.get_or_create(user=user)
        response_params = 'state={}&access_token={}&token_type=Token'.format(state, token.key)
        return HttpResponseRedirect('{}#{}'.format(redirect_to, response_params))