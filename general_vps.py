from django.conf import settings
from subprocess import check_output
import requests

class VPS:
    scripts = {
        'getuser' : '/usr/share/nginx/html/api-get-user.php',
        'formsubmissions' : '/usr/share/nginx/html/api-get-form-submissions.php',
        'auth' : '/usr/share/nginx/html/api-ext-auth.php',
    }
    @staticmethod
    def executeCommand(command, **kwargs):
        if command not in ['getuser', 'formsubmissions', 'auth']:
            return None

        if settings.DEBUG:
            url = "http://127.0.0.1:5000"
        else:
            url = "http://10.3.3.11:5000"

        kwargs['key'] = settings.API_KEY

        if command == 'auth':
            if 'otp' in kwargs and kwargs.get('otp', None) == None:
                del kwargs['otp']

            r = requests.post(url + "/login", json=kwargs)
            if r.status_code == 200:
                return r.json()
            return None
        elif command == 'formsubmissions':
            kwargs['id'] = str(kwargs['id'])
            r = requests.get(url + "/form", params=kwargs)
            if r.status_code == 200:
                return r.json()
            return None
        elif command == 'getuser':
            r = requests.get(url + "/user/info", params=kwargs)
            if r.status_code == 200:
                return r.json()
            return None
        return None
