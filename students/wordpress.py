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

    @staticmethod
    def merge_subscriptions(props, submissions):
        def to_int(n):
            try:
                return int(n)
            except:
                return n
        #requires list output from get_subscriptions. does a logical OR on all submissions
        #build dictionary
        submissions_dict = {}
        user_id_index = props.index("user_id")
        for submission in submissions:
            #convert all numbers in strings to actual numbers
            submission = list(map(to_int, submission))
            try:
                submissions_dict[submission[user_id_index]].append(submission)
            except KeyError:
                submissions_dict[submission[user_id_index]] = [submission]

        #logical OR on all
        results = []
        for person in submissions_dict.values():
            person_merged = []
            for i in range(len(person[0])):
                #merge all integers using logical OR, skip user_id
                if i == props.index("user_id"):
                    person_merged.append(person[0][i])
                    continue
                if type(person[0][i]) == int:
                    person_merged.append(int(any([x[i] for x in person])))
                else:
                    #if not integer take first submission by default
                    person_merged.append(person[0][i])
            results.append(person_merged)

        #return it in same format
        return results