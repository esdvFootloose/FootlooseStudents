from django.contrib.auth.models import User
import json
import logging
from django.conf import settings
from FootlooseStudents.secret import STUDENT_LOGIN_DISABLED
from general_vps import VPS

logger = logging.getLogger('django')

class WordpressAuthBackend:
    def authenticate(self, request, username=None, password=None):
        if username is None or password is None:
            return None
        if settings.DEBUG:
            cmd = [username, password.replace('&', '\&').replace('$', '\$')]
        else:
            cmd = [username, password]

        wp_user = VPS.executeCommand('auth', cmd)
        try:
            wp_user = json.loads(wp_user)
        except:
            return None

        if STUDENT_LOGIN_DISABLED:
            if 'administrator' not in wp_user['roles'] and 'um_bestuur' not in wp_user['roles']:
                return None
        try:
            django_user = User.objects.get(username=wp_user['username'])
        except User.DoesNotExist:
            try:
               django_user = User.objects.get(email=wp_user['email'])
            except User.DoesNotExist:
                django_user = User(username=wp_user['username'], email=wp_user['email'])
        django_user.username = wp_user['username']
        django_user.email = wp_user['email']
        if 'administrator' in wp_user['roles'] or 'um_bestuur' in wp_user['roles']:
            django_user.is_staff = True
            django_user.is_superuser = True
        django_user.save()
        return django_user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
