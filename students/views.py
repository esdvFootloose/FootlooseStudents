from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from subprocess import check_output
import json
import csv
from django.http import HttpResponse

def get_students_data():
    if settings.DEBUG:
        props = check_output(['ssh', 'footloosedirect', 'php', '/usr/share/nginx/html/api-get-user.php', 'props'])
    else:
        props = check_output(['php', '/usr/share/nginx/html/api-get-user.php', 'props'])
    props = json.loads(props.decode())
    #remove/move the list a bit
    props.remove('roles')

    if settings.DEBUG:
        students = check_output(['ssh', 'footloosedirect', 'php', '/usr/share/nginx/html/api-get-user.php'])
    else:
        students = check_output(['php', '/usr/share/nginx/html/api-get-user.php'])

    students = json.loads(students.decode())

    data = []
    for student in students:
        if 'lid' not in ''.join(student['roles']):
            continue
        student_data = []
        for prop in props:
            student_data.append(student[prop])
        data.append(student_data)

    return props, data

@staff_member_required
def list_all_students_csv(request):
    props, students = get_students_data()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(props)
    for student in students:
        writer.writerow(student)

    return response

@staff_member_required
def list_all_students(request):
    props, data = get_students_data()

    return render(request, 'list_al_students.html', {
        'props' : props,
        'students' : data,
    })

