from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseBadRequest, HttpResponse
from students.models import StudentMeta
from .models import CourseType, Course

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
def list_course_types(request):
    return render(request, 'list_courses.html', {
        'coursetypes': CourseType.objects.all()
    })

@staff_member_required
def manual_distribute(request, pk):
    ctype = get_object_or_404(CourseType, pk=pk)
