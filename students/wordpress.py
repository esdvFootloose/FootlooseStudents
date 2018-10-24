import json
from general_vps import VPS
from django.core.cache import cache
import re

class WordPress:
    @staticmethod
    def get_students_data(username=None, as_dict=False):
        if username is None and not as_dict:
            cdata = cache.get('wordpress_student_data')
            if cdata is not None:
                return cdata[0], cdata[1]

        props = json.loads(VPS.executeCommand('getuser', ['props']))
        #remove/move the list a bit
        props.remove('roles')

        cmd = []
        if username is not None:
            cmd += [username]
        students = json.loads(VPS.executeCommand('getuser', cmd))

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

        if username is None and not as_dict:
            cache.set('wordpress_student_data', (props, data), 24*60*60) #cache for 24 hours

        return props, data

    @staticmethod
    def get_subscriptions(formid, as_dict=False):
        submissions = json.loads(VPS.executeCommand('formsubmissions', [str(formid)]))

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
    def get_interested_members(formid):
        cdata = cache.get('wordpress_student_interested')
        if cdata is not None:
            return cdata

        submissions = json.loads(VPS.executeCommand('formsubmissions', [str(formid)]))

        committees = {}
        for sub in submissions:
            name = sub['submitter']
            email = sub['email_address']
            interest = sub['i_might_be_interested_in_the_following_committee_s_and_would_like_to_receive_more_information_about_it']
            for comm in re.findall(r'".*?"', interest):
                comm = comm.strip('"')
                if comm not in committees:
                    committees[comm] = []
                committees[comm].append((name, email))

        cache.set('wordpress_student_interested', committees, 24*60*60) #cache for 24 hours

        return committees

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