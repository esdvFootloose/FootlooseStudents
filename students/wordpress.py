import json
from general_vps import VPS
from django.core.cache import cache
import re

class WordPress:
    @staticmethod
    def get_students_data(username=None, as_dict=False, board=False):
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
            if not board:
                if 'lid' not in ''.join(student['roles']):
                    continue
            else:
                if 'commissie' in student['nickname'] or 'bestuur' in student['nickname'].lower():
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
            if 'consent' in p:
                p = 'consent'
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
                    sub_data.append('0')
                if sub_data[-1] == '' and 'partner' not in prop:
                    sub_data[-1] = '0'
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
            if len(person) > 1:
                #merge is needed
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
                #do overriding string merge on partners
                pi = props.index("partner")
                person_merged[pi] = " | ".join([x[pi] for x in person])
            else:
                #no merge necesarry
                person_merged = person[0]


            results.append(person_merged)

        #return it in same format
        return results