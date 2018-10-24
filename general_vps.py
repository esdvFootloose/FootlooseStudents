from django.conf import settings
from subprocess import check_output

class VPS:
    scripts = {
        'getuser' : '/usr/share/nginx/html/api-get-user.php',
        'formsubmissions' : '/usr/share/nginx/html/api-get-form-submissions.php',
        'auth' : '/usr/share/nginx/html/api-ext-auth.php',
    }
    @staticmethod
    def executeCommand(command, args):
        if command not in VPS.scripts or type(args) != list:
            return None

        if settings.DEBUG:
            cmd = ['ssh', 'footloosedirect', 'php', VPS.scripts[command]] + args
        else:
            cmd = ['php', VPS.scripts[command]] + args

        return check_output(cmd).decode()