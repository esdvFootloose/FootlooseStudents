from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseBadRequest, HttpResponse
from students.models import StudentMeta
from .models import CourseType, Course, Couple, Distribution
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from .util import create_couple_block

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
def list_course_types(request):
    return render(request, 'list_courses.html', {
        'coursetypes': CourseType.objects.all()
    })

@staff_member_required
def manual_distribute(request, pk):
    ctype = get_object_or_404(CourseType, pk=pk)
    return render(request, 'distribution.html', {
        'type': ctype,
        'courses': ctype.course_set.all(),
        'users': User.objects.all()
    })