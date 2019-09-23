import json
from general_vps import VPS
from django.core.cache import cache
import re
from itertools import groupby
from general_util import get_academic_year

class WordPress:
    @staticmethod
    def get_students_data(username=None, as_dict=False, board=False, year=None, use_cache=True):
        if use_cache:
            cdata = cache.get('wordpress_student_data_{}'.format(as_dict))
            if cdata is not None:
                if username is None:
                    return cdata[0], cdata[1]
                else:
                    for d in cdata[1]:
                        if d['nickname'] == username:
                            return cdata[0], [d]



        props = json.loads(VPS.executeCommand('getuser', ['props']))
        #remove/move the list a bit
        props.remove('roles')
        if year is None:
            begin, end = get_academic_year()
        else:
            begin, end = year
        cmd = []
        if username is not None:
            cmd += [username]
        students_raw = json.loads(VPS.executeCommand('getuser', cmd))

        students = []
        for student in students_raw:
            if not board:
                roles = set(student['roles'])
                if len(roles & {'um_betaald-lid-{}-{}'.format(begin.year, end.year),
                                'um_onbetaald-lid-{}-{}'.format(begin.year, end.year), 'um_bestuur', 'administrator' }) == 0:
                    continue
            else:
                if 'commissie' in student['nickname'] or 'bestuur' in student['nickname'].lower():
                    continue
            students.append(student)

        if as_dict:
            if username is None:
                cache.set('wordpress_student_data_{}'.format(as_dict), (props, students),
                          24 * 60 * 60)  # cache for 24 hours
            return props, students

        data = []
        for student in students:
            student_data = []
            for prop in props:
                student_data.append(student[prop])
            data.append(student_data)

        if username is None:
            cache.set('wordpress_student_data_{}'.format(as_dict), (props, data), 24*60*60) #cache for 24 hours

        return props, data

    @staticmethod
    def get_subscriptions(formid, as_dict=False):
        submissions = json.loads(VPS.executeCommand('formsubmissions', [str(formid)]))

        props = ['user_id', 'first_name', 'last_name', 'emailadres','student']
        for p in  sorted([x for x in list(submissions[0].keys()) if x not in props]):
            if p == 'policy':
                continue
            props.append(p)
        if as_dict:
            return props, submissions

        props.remove('')
        if '_edit' not in props:
            props.append('_edit')
        data = []
        for sub in submissions:
            sub_data = []
            for prop in props:
                try:
                    sub_data.append(sub[prop])
                except KeyError:
                    sub_data.append('')
            try:
                sub_data[props.index('_edit')] = int(sub_data[props.index('_edit')].split(':')[0])
            except ValueError:
                sub_data[props.index('_edit')] = -1
            data.append(sub_data)

        return props, data

    @staticmethod
    def get_subscriptions_objects(props, subscriptions=None):
        if subscriptions is None:
            subscriptions = props[1]
            props = props[0]
        sub_objects = []
        subscriptions = [list(g) for k, g in groupby(sorted(subscriptions, key=lambda x: (x[props.index('user_id')],
                                                                                          x[props.index('_edit')])),
                                                     lambda x: x[0])]

        for sub in subscriptions:
            sub = sub[-1] # filter the latest submission
            obj = {
                'courses' : [[None, None] for i in range(6)]
            }
            for prop in sorted(props):
                if prop in ['user_id', 'first_name', 'last_name', 'emailadres', 'student']:
                    obj[prop] = sub[props.index(prop)]
                    continue

                if 'course_choice' in prop:
                    course_num = int(prop.split('_')[-1])
                    obj['courses'][course_num-1][0] = sub[props.index(prop)]
                    continue

                if 'dance_partner' in prop and 'alumni' not in prop:
                    course_num = int(prop.split('_')[-1])
                    obj['courses'][course_num-1][1] = sub[props.index(prop)]
                    continue
            sub_objects.append(obj)


        return sub_objects


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

    # @staticmethod
    # def merge_subscriptions(props, submissions):
    #     def to_int(n):
    #         try:
    #             return int(n)
    #         except:
    #             return n
    #     #requires list output from get_subscriptions. does a logical OR on all submissions
    #     #build dictionary
    #     submissions_dict = {}
    #     user_id_index = props.index("user_id")
    #     for submission in submissions:
    #         #convert all numbers in strings to actual numbers
    #         submission = list(map(to_int, submission))
    #         try:
    #             submissions_dict[submission[user_id_index]].append(submission)
    #         except KeyError:
    #             submissions_dict[submission[user_id_index]] = [submission]
    #
    #     #logical OR on all
    #     results = []
    #     for person in submissions_dict.values():
    #         person_merged = []
    #         if len(person) > 1:
    #             #merge is needed
    #             for i in range(len(person[0])):
    #                 #merge all integers using logical OR, skip user_id
    #                 if i == props.index("user_id"):
    #                     person_merged.append(person[0][i])
    #                     continue
    #                 if type(person[0][i]) == int:
    #                     person_merged.append(int(any([x[i] for x in person])))
    #                 else:
    #                     #if not integer take first submission by default
    #                     person_merged.append(person[0][i])
    #             #do overriding string merge on partners
    #             # pi = props.index("partner")
    #             # person_merged[pi] = " | ".join([x[pi] for x in person])
    #         else:
    #             #no merge necesarry
    #             person_merged = person[0]
    #
    #
    #         results.append(person_merged)
    #
    #     #return it in same format
    #     return results