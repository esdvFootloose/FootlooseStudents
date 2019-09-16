from django.contrib.auth.models import User
from distribution.models import Course
from students.models import StudentMeta
from datetime import date
import json
import random
from django.db.models import Q

def generate_users():

    for i in range(100):
        if i < 50:
            usr = User(first_name=str(i), last_name="Eindhoven", email="{}@eindhoven.com".format(i), username="Eindhoven{}".format(i))
            usr.save()
            meta = StudentMeta(user=usr, is_student=True, userid=i, institute="Eindhoven University of Technology")
            # eindhoven students
            if i < 10:
                # active member
                meta.is_activemember = True
            meta.save()
        elif i >= 50 and i < 75:
            usr = User(first_name=str(i), last_name="Student", email="{}@student.com".format(i), username="Student{}".format(i))
            usr.save()
            meta = StudentMeta(user=usr, is_student=True, userid=i, institute="ergens")
            meta.save()
        else:
            usr = User(first_name=str(i), last_name="Eindhoven", email="{}@eindhoven.com".format(i), username="other{}".format(i))
            usr.save()
            meta = StudentMeta(user=usr, is_student=False, userid=i)
            meta.save()


def get_name(usr):
    return "{} {}".format(usr.first_name, usr.last_name)


def generate_subscriptions():
    subscriptions = []
    courses = list(Course.objects.all())

    for usr in User.objects.filter(is_staff=False):
        partners = list(User.objects.filter(Q(is_staff=False) & ~Q(studentmeta__userid=usr.studentmeta.userid)).order_by('?')[:6])
        subscriptions.append({
            'emailadres': usr.email,
            'first_name': usr.first_name,
            'last_name': usr.last_name,
            'student': usr.studentmeta.is_student,
            'user_id': usr.studentmeta.userid,
            'courses': [[str(random.choice(courses)), get_name(partners.pop(0))] for i in range(3)] + [['none','']*3]
        })

    with open('test_subscriptions.json', 'w') as stream:
        stream.write(json.dumps(subscriptions))
