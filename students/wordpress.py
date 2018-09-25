from django.conf import settings
from subprocess import check_output
import json

class WordPress:
    @staticmethod
    def get_students_data(username=None, as_dict=False):
        if settings.DEBUG:
            props = check_output(['ssh', 'footloosedirect', 'php', '/usr/share/nginx/html/api-get-user.php', 'props'])
        else:
            props = check_output(['php', '/usr/share/nginx/html/api-get-user.php', 'props'])
        props = json.loads(props.decode())
        #remove/move the list a bit
        props.remove('roles')


        if settings.DEBUG:
            cmd = ['ssh', 'footloosedirect', 'php', '/usr/share/nginx/html/api-get-user.php']
        else:
            cmd = ['php', '/usr/share/nginx/html/api-get-user.php']

        if username is not None:
            cmd += [username]

        students = check_output(cmd)

        students = json.loads(students.decode())

        if as_dict:
            return props, students

        data = []
        for student in students:
            if 'lid' not in ''.join(student['roles']):
                continue
            student_data = []
            for prop in props:
                student_data.append(student[prop])
            data.append(student_data)

        return props, data

    @staticmethod
    def get_subscriptions(formid, as_dict=False):
        if settings.DEBUG:
            cmd = ['ssh', 'footloosedirect', 'php', '/usr/share/nginx/html/api-get-form-submissions.php', str(formid)]
        else:
            cmd = ['php', '/usr/share/nginx/html/api-get-form-submissions.php', str(formid)]

        submissions = json.loads(check_output(cmd).decode())
        props = ['user_id', 'first_name', 'last_name', 'emailadres','student']
        for p in  sorted([x for x in list(submissions[0].keys()) if x not in props]):
            if p == 'policy' or p == 'partner':
                continue
            props.append(p)
        props.append('partner')
        if as_dict:
            return props, submissions

        data = []
        for sub in submissions:
            sub_data = []
            for prop in props:
                try:
                    sub_data.append(sub[prop])
                except KeyError:
                    sub_data.append('-')
            data.append(sub_data)

        return props, data