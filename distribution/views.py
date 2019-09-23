from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseBadRequest, HttpResponse
from students.models import StudentMeta
from .models import CourseType, Course, Couple, Distribution
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from .util import create_couple_block
import json
from students.wordpress import WordPress
import unicodedata
from django import forms
import random
from .forms import Confirm

def strip_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')

@staff_member_required
def api_toggle_active_member(request):
    id = request.GET.get('id', -1)

    if id == -1:
        return HttpResponseBadRequest()

    try:
        meta = StudentMeta.objects.get(userid=id)
    except StudentMeta.DoesNotExist:
        return HttpResponseBadRequest()

    meta.is_activemember = not meta.is_activemember
    meta.save()

    return HttpResponse("done")

@staff_member_required
def api_toggle_student(request):
    id = request.GET.get('id', -1)

    if id == -1:
        return HttpResponseBadRequest()

    try:
        meta = StudentMeta.objects.get(userid=id)
    except StudentMeta.DoesNotExist:
        return HttpResponseBadRequest()

    meta.is_student = not meta.is_student
    meta.save()

    return HttpResponse("done")

@staff_member_required
@require_POST
def api_create_couple(request):
    leader = get_object_or_404(User, pk=request.POST['leaderid'])
    if request.POST['followerid'] != '-1':
        follower = get_object_or_404(User, pk=request.POST['followerid'])
    else:
        follower = None

    couple = Couple.objects.get_or_create(leader=leader, follower=follower)[0]

    return HttpResponse(create_couple_block(couple))

@staff_member_required
@require_POST
def api_save_distributions(request, pk):
    course = get_object_or_404(Course, pk=pk)
    data = json.loads(request.POST['data'])
    if None in data['couples']:
        data['couples'].remove(None)
    t = bool(data['admitted'])
    for distr in Distribution.objects.filter(course=course, admitted=t):
        if distr.couple.pk not in data['couples']:
            try:
                distr.delete()
            except:
                return HttpResponse("Database error when deleting distribution for course {} {}".format(course,
                                                                                                      "admitted" if t else "rejected"))
    for couple_pk in set(data['couples']):
        couple = get_object_or_404(Couple, pk=couple_pk)
        if Distribution.objects.filter(couple=couple, course=course, admitted=t).exists():
            continue
        try:
            Distribution(couple=couple, course=course, reason=0, admitted=t).save()
        except:
            return HttpResponse("Database error when saving distribution for course {} {}".format(course, "admitted" if t else "rejected"))

    return HttpResponse("Saved course {} {}".format(course, "admitted" if t else "rejected"))


@staff_member_required
def list_course_types(request):
    return render(request, 'list_courses.html', {
        'coursetypes': CourseType.objects.all()
    })

@staff_member_required
def manual_distribute(request, pk):
    ctype = get_object_or_404(CourseType, pk=pk)
    courses = []
    for c in ctype.course_set.all():
        courses.append([
            c,
            c.distributions.filter(admitted=True),
            c.distributions.filter(admitted=False),
        ])

    return render(request, 'distribution.html', {
        'type': ctype,
        'courses': courses,
        'users': User.objects.all()
    })

def create_couples_from_submissions(objects, matched_persons={}):
    subscriptions_per_course = {}

    # convert data to per course basis
    for object in objects:
        for course in object['courses']:
            if course[0] == 'none':
                continue
            if course[0] not in subscriptions_per_course:
                subscriptions_per_course[course[0]] = []
            subscriptions_per_course[course[0]].append([object['user_id'], course[1]])

    nonmatchable_persons = []
    subscriptions_per_course_couples = {}

    # match and create all couples if applicable
    for course, couples in subscriptions_per_course.items():
        for i, couple in enumerate(couples):
            # we do not actually ask at subscription who is follower and leader, just partner
            # so the distinction here is arbitrairy and simply for better db representation

            try:
                leader = User.objects.get(studentmeta__userid=int(couple[0]))
            except User.DoesNotExist:
                # this should not happend, invalid entry so skip
                continue

            if couple[1].strip() != '':
                # (fuzzy) search the text partner
                name = strip_accents(couple[1]).replace(' ', '').lower()
                if matched_persons.get(name, [''])[0] != '':
                    follower = User.objects.get(pk=int(matched_persons[name][0]))
                else:
                    try:
                        follower = User.objects.get(username=name)
                    except (User.DoesNotExist, User.MultipleObjectsReturned):
                        try:
                            follower = User.objects.get(username__contains=name)
                        except (User.DoesNotExist, User.MultipleObjectsReturned):
                            # fuzzy search needed
                            nonmatchable_persons.append(couple[1])
                            continue


                # see if this couple already exists
                try:
                    couple_obj = Couple.objects.get(leader=leader, follower=follower)
                except Couple.DoesNotExist:
                    try:
                        couple_obj = Couple.objects.get(leader=follower, follower=leader)
                    except Couple.DoesNotExist:
                        # does not exists so create
                        couple_obj = Couple(leader=leader, follower=follower)
                        couple_obj.save()
            else:
                follower = None
                try:
                    couple_obj = Couple.objects.get(leader=leader, follower__isnull=True)
                except Couple.DoesNotExist:
                    couple_obj = Couple(leader=leader)
                    couple_obj.save()

            if course not in subscriptions_per_course_couples:
                subscriptions_per_course_couples[course] = []
            if couple_obj not in subscriptions_per_course_couples[course]:
                subscriptions_per_course_couples[course].append(couple_obj)

    return subscriptions_per_course_couples, nonmatchable_persons


@staff_member_required
def automatic_distribute_step1(request):
    if request.method != "POST":
        return render(request, 'confirm.html', {
            'subject': 'This will delete all existing distributions and couples, please confirm',
            'form': Confirm()
        })
    form = Confirm(request.POST)
    if not form.is_valid():
        return render(request, 'confirm.html', {
            'subject': 'This will delete all existing distributions and couples, please confirm',
            'form': form
        })

    Distribution.objects.all().delete()
    nonmatchable_persons = create_couples_from_submissions(
            WordPress.get_subscriptions_objects(WordPress.get_subscriptions(9)))[1]
    form = forms.Form()
    for person in nonmatchable_persons:
        name = strip_accents(person).replace(' ', '').lower()
        form.fields[name] = forms.ModelChoiceField(User.objects.all(), label=person)
        form.fields[name].required = False

    return render(request, 'automatic_distribute_step.html', {
        'users': User.objects.all(),
        'form': form
    })


@staff_member_required
@require_POST
def automatic_distribute_step2(request):

    subscriptions_per_course_couples = create_couples_from_submissions(
            WordPress.get_subscriptions_objects(WordPress.get_subscriptions(9)), dict(request.POST)
        )[0]

    for coursename, couples in subscriptions_per_course_couples.items():
        ctype = CourseType.objects.get(name=coursename.split(' ')[0].lower())
        try:
            course = Course.objects.get(name=ctype, level=int(coursename.split(' ')[-1]))
        except:
            course = Course.objects.get(name=ctype, levelname=''.join(coursename.split(' ')[1:]).lower())

        r = random.SystemRandom()

        active_members = [c for c in couples if c.get_highest_status() == "active_member"]
        r.shuffle(active_members)
        students_eindhoven = [c for c in couples if c.get_highest_status() == "student_eindhoven"]
        r.shuffle(students_eindhoven)
        students = [c for c in couples if c.get_highest_status() == "student"]
        r.shuffle(students)
        other = [c for c in couples if c.get_highest_status() not in  ["active_member", "student", "student_eindhoven"]]
        r.shuffle(other)

        total = active_members + students_eindhoven + students + other

        for couple in total[:course.limit]:
            Distribution(couple=couple, course=course, reason=1, admitted=True).save()

        for couple in total[course.limit:]:
            Distribution(couple=couple, course=course, reason=1, admitted=False).save()




    return render(request, 'base.html', {
        'message': 'Distribution done, you can view it at manual distribution menu'
    })