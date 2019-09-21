from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseBadRequest, HttpResponse
from students.models import StudentMeta
from .models import CourseType, Course, Couple, Distribution
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from .util import create_couple_block
import json

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
    follower = get_object_or_404(User, pk=request.POST['followerid'])

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