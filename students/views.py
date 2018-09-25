from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from subprocess import check_output
import json
import csv
from django.http import HttpResponse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import Confirmation
from general_mail import send_mail

def get_students_data(username=None, as_dict=False):
    if settings.DEBUG:
        props = check_output(['ssh', 'footloosedirect', 'php', '/usr/share/nginx/html/api-get-user.php', 'props'])
    else:
        props = check_output(['php', '/usr/share/nginx/html/api-get-user.php', 'props'])
    props = json.loads(props.decode())
    #remove/move the list a bit
    props.remove('roles')


    if settings.DEBUG:
        cmd = ['ssh', 'footloosedirect', 'php', '/usr/share/nginx/html/api-get-user.php']
    else:
        cmd = ['php', '/usr/share/nginx/html/api-get-user.php']

    if username is not None:
        cmd += [username]

    students = check_output(cmd)

    students = json.loads(students.decode())

    if as_dict:
        return props, students

    data = []
    for student in students:
        if 'lid' not in ''.join(student['roles']):
            continue
        student_data = []
        for prop in props:
            student_data.append(student[prop])
        data.append(student_data)

    return props, data

def get_subscriptions(formid, as_dict=False):
    if settings.DEBUG:
        cmd = ['ssh', 'footloosedirect', 'php', '/usr/share/nginx/html/api-get-form-submissions.php', str(formid)]
    else:
        cmd = ['php', '/usr/share/nginx/html/api-get-form-submissions.php', str(formid)]

    submissions = json.loads(check_output(cmd).decode())
    props = list(submissions[0].keys())

    if as_dict:
        return props, submissions

    data = []
    for sub in submissions:
        sub_data = []
        for prop in props:
            try:
                sub_data.append(sub[prop])
            except KeyError:
                sub_data.append('-')
        data.append(sub_data)

    return props, data

@staff_member_required
def list_all_submissions_csv(request):
    props, submissions = get_subscriptions(3)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="submissions.csv"'

    writer = csv.writer(response)
    writer.writerow(props)
    for submission in submissions:
        writer.writerow(submission)

    return response


@staff_member_required
def list_all_submissions(request):
    props, submissions = get_subscriptions(3)

    return render(request, 'list_al_submissions.html', {
        'props' : props,
        'submissions' : submissions,
    })


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

def get_academic_year():
    today = date.today()

    if today.month < 9: #before september
        begin = date(today.year - 1,9,1)
        end = date(today.year, 8, 31)
    else:
        begin = date(today.year,9,1)
        end = date(today.year+1,8,31)

    return begin, end


@login_required
def verify_student_request(request):
    if request.user.is_staff:
        return render(request, 'base.html', {
            'message' : 'Only for students'
        })
    begin, end = get_academic_year()
    props, data = get_students_data(request.user.username, as_dict=True)
    data = data[0]
    if request.user.confirmations.filter(date__gt=begin, date__lt=end).count() > 0:
        return render(request, 'base.html', {
            'message' : 'You are already verified as student of {}!'.format(data['footloose_institution'])
        })
    if request.method != 'POST':
        if data['footloose_student'].lower() == 'no':
            return render(request, 'base.html', {
                'message' : 'You have put on your subscription that you are not a student and thus cant verify. If this was in error contact ict@esdvfootloose.nl'
            })
        if data['footloose_institution'] == 'other':
            return render(request, 'base.html', {
                'message' : 'Only TU/e and Fontys currently supported, you have put on your subscription you are from other institute. If this was in error contact ict@esdvfootloose.nl'
            })

        return render(request, 'request_verify.html', {
            'email' : data['footloose_tuemail_verific'] if data['footloose_institution'] == 'Eindhoven University of Technology' else data['footloose_fontys_verific'],
            'institute' : data['footloose_institution']
        })


    generator = PasswordResetTokenGenerator()
    token = generator.make_token(request.user)
    if settings.DEBUG:
        url = 'http://localhost:8080/students/verify/confirm/{}/'.format(token)
    else:
        url = 'https://students.edsvfootloose.nl/students/verify/confirm/{}/'.format(token)

    send_mail('Footloose Student Verification', 'mail/verify.html', {'url' : url}, data['footloose_tuemail_verific'] if data['footloose_institution'] == 'Eindhoven University of Technology' else data['footloose_fontys_verific'])

    return render(request, 'base.html', { 'message' : 'Verification link send' })



@login_required
def verify_student_confirm(request, token):
    begin, end = get_academic_year()
    props, data = get_students_data(request.user.username, as_dict=True)
    data = data[0]
    if request.user.confirmations.filter(date__gt=begin, date__lt=end).count() > 0:
        return render(request, 'base.html', {
            'message' : 'You are already verified as student of {}!'.format(data['footloose_institution'])
        })

    generator = PasswordResetTokenGenerator()

    if not generator.check_token(request.user, token):
        return render(request, 'base.html', {
            'message' : 'Invalid token!'
        })

    #TODO: save the email with which the token was requested to make security tight
    c = Confirmation(date=date.today(), user=request.user, email=data['footloose_tuemail_verific'] if data['footloose_institution'] == 'Eindhoven University of Technology' else data['footloose_fontys_verific'])
    c.save()

    return render(request, 'base.html', {
        'message' : 'Email verified! You can now close this tab.'
    })