import requests
from django.contrib.auth.backends import BaseBackend
from .models import User
from requests.auth import HTTPBasicAuth
from django.contrib.auth.hashers import check_password


class ApiBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username == 'admin':
            user = User.objects.get(username = 'admin')
            if check_password(password, user.password):
                return user
        
        auth = HTTPBasicAuth(username, password)

        response = requests.post('https://api.ldap.groupe-hasnaoui.com/pumaprd/auth', auth=auth)

        if response.status_code == 200 and response.json().get('authenticated'):
            user = User.objects.get(username = response.json().get('userinfo')['ad2000'])
            return user

        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
