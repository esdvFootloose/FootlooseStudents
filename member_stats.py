import os
import django
from datetime import date
import json

if os.getenv('DJANGO_SETTINGS_MODULE') is None:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'FootlooseStudents.settings_development'

django.setup()

from distribution.models import Distribution
from students.wordpress import WordPress


def calculate_age(born):
    today = date(year=2019, month=9, day=1)
    if today.replace(year=born.year) < today:
        # birthday already passed
        return today.year - born. year
    else:
        return today.year - born.year - 1

distrs = Distribution.objects.filter(admitted=True)

boundary_year = date.today().year - 21
admitted_users = {}
# warm the cache
WordPress.get_students_data(as_dict=True)
for distr in distrs:
    usrs =[distr.couple.leader]
    if distr.couple.follower is not None:
        usrs.append(distr.couple.follower)
    for usr in usrs:
        if usr.username not in admitted_users:
            try:
                d = WordPress.get_students_data(username=usr.username, as_dict=True)[1][0]
            except IndexError:
                continue
            bday = d['birth_date']
            bday = date(year=int(bday.split('/')[0]), month=int(bday.split('/')[1]), day=int(bday.split('/')[2]))
            admitted_users[usr.username] = {
                'numcourses' : 0,
                'age': calculate_age(bday),
                'student': usr.studentmeta.is_student
            }
        admitted_users[usr.username]['numcourses'] += 1


membership_cost = 40
first_course_cost_student = 30
first_course_cost_nonstudent = 40
other_course_cost_student = 20
other_course_cost_nonstudent = 30

print(json.dumps(admitted_users))