from general_vps import VPS
from django.core.cache import cache
import re
from itertools import groupby
from general_util import get_academic_year
# import pytz
# from datetime import datetime

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



        props = VPS.executeCommand('getuser', username='props')
        #remove/move the list a bit
        props.remove('roles')
        if year is None:
            begin, end = get_academic_year()
        else:
            begin, end = year

        if username is not None:
            students_raw = VPS.executeCommand('getuser', username=username)
        else:
            students_raw = VPS.executeCommand('getuser')


        students = []
        for student in students_raw:
            if student['nickname'] == False:
                continue
            if not board:
                roles = set(student['roles'])
                if len(roles & {'um_betaald-lid-{}-{}'.format(begin.year, end.year),
                                'um_onbetaald-lid-{}-{}'.format(begin.year, end.year), 'um_bestuur', 'administrator', 'um_te-laat' }) == 0:
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
    def get_subscriptions(formid, aslist=False):
        submissions_raw = VPS.executeCommand('formsubmissions', id=formid)

        to_bool = lambda x: True if x == '1' else False

        # props = ['user_id', 'first_name', 'last_name', 'emailadres','student']
        # for p in  sorted([x for x in list(submissions[0].keys()) if x not in props]):
        #     if p != '' and p[0] != '_' and len(p.split('_')) < 4:
        #         props.append(p)
        submissions_all = []
        props = [
        'user_id',
        'seqid',
        'first_name',
        'last_name',
        'student',
        # 'time',
        'emailadres',
        'modern_1',
        'modern_2',
        'modern_3',
        'ballet_1',
        'ballet_2',
        'ballet_3',
        'hiphop_1',
        'hiphop_2',
        'hiphop_3',
        'zouk_1',
        'zouk_2',
        'zouk_3',
        'hiphop_demoteam',
        'project_sputnik',
        'salsa_1',
        'salsa_2',
        'salsa_3',
        'salsa_4',
        'ballroom_bronze',
        'ballroom_silver',
        'ballroom_silverstar',
        'ballroom_gold',
        'ballroom_topclass',
        'ballroom_alumni',
        'partners',
        ]
        for sub in submissions_raw:
            # because of subtle differences in the wordpress setup do hardcoded conversion here
            submissions_all.append({
                'user_id': int(sub['user_id']),
                'seqid': int(sub['_seq']),
                'first_name': sub['first_name'],
                'last_name': sub['last_name'],
                'student': sub['student'],
                # 'time': pytz.timezone("UTC").localize(datetime.fromtimestamp(int(sub['_edit'].split(':')[0])))
                #     .astimezone(pytz.timezone("Europe/Amsterdam")),
                'emailadres': sub['emailadres'],
                'modern_1': to_bool(sub['modern_jazz_1']),
                'modern_2': to_bool(sub['modern_jazz_2']),
                'modern_3': to_bool(sub['modern_3']),
                'ballet_1': to_bool(sub['ballet_1']),
                'ballet_2': to_bool(sub['ballet_2']),
                'ballet_3': to_bool(sub['ballet_3']),
                'hiphop_1': to_bool(sub['hiphop_1']),
                'hiphop_2': to_bool(sub['hiphop_2']),
                'hiphop_3': to_bool(sub['hiphop_3']),
                'zouk_1': to_bool(sub['zouk_1']),
                'zouk_2': to_bool(sub['zouk_2']),
                'zouk_3': to_bool(sub['zouk_3']),
                'hiphop_demoteam': to_bool(sub['hiphop_demo_team']),
                'project_sputnik': to_bool(sub['project_sputnik']),
                'salsa_1': to_bool(sub['salsa_1']),
                'salsa_2': to_bool(sub['salsa_2']),
                'salsa_3': to_bool(sub['salsa_3']),
                'salsa_4': to_bool(sub['salsa_3']),
                'ballroom_bronze': to_bool(sub['ballroom_bronze']),
                'ballroom_silver': to_bool(sub['ballroom_silver']),
                'ballroom_silverstar': to_bool(sub['ballroom_silverstar']),
                'ballroom_gold': to_bool(sub['ballroom_gold']),
                'ballroom_topclass': to_bool(sub['ballroom_topclass']),
                'ballroom_alumni': to_bool(sub['ballroom_alumni_reuenisten']),
                'partners': sub['please_indicate_per_dance_course_who_your_dance_partner_is_going_to_be_leave_blank_if_you_haven_t_found_a_dance_partner_yet_or_if_a_dance_partner_is_not_applicable_for_your_course']
            })

        # filter out all double submissions, simply ignore everything before last one
        #  sort first by user_id then by sequence id
        submissions_all = sorted(submissions_all, key=lambda x: (x['user_id'], x['seqid']), reverse=True)
        #  groupby and select only the first (because sorted so highest sequence id)
        submission_filter = [list(group)[0] for key, group in groupby(submissions_all, lambda x: x['user_id'])]
        #  sort by user_id again
        submission_filter = sorted(submission_filter, key=lambda x: x['user_id'])

        if not aslist:
            return props, submission_filter
        else:
            return props, [[sub[p] for p in props] for sub in submission_filter]

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

        submissions = VPS.executeCommand('formsubmissions', id=formid)

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
