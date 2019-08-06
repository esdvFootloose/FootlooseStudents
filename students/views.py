from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import csv
from django.http import HttpResponse
from .util import VerifyTokenGenerator
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import Confirmation
from general_mail import send_mail
from .wordpress import WordPress


@staff_member_required
def list_all_submissions_csv(request):
    props, submissions = WordPress.get_subscriptions(3)
    # submissions_merged = WordPress.merge_subscriptions(props, submissions)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="submissions.csv"'

    writer = csv.writer(response)
    writer.writerow(props)
    for submission in submissions:
        writer.writerow(submission)

    return response

@staff_member_required
def list_all_submissions_unmerged_csv(request):
    props, submissions = WordPress.get_subscriptions(3)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="submissions.csv"'

    writer = csv.writer(response)
    writer.writerow(props)
    for submission in submissions:
        writer.writerow(submission)

    return response

@staff_member_required
def list_all_submissions(request):
    props, submissions = WordPress.get_subscriptions(9)
    # submissions_merged = WordPress.merge_subscriptions(props, submissions)

    return render(request, 'list_al_submissions.html', {
        'props' : props,
        'submissions' : submissions,
    })


@staff_member_required
def list_all_students_csv(request):
    props, students = WordPress.get_students_data()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(props)
    for student in students:
        writer.writerow(student)

    return response

@staff_member_required
def list_all_students(request):
    props, data = WordPress.get_students_data()

    return render(request, 'list_al_students.html', {
        'props' : props,
        'students' : data,
    })

@staff_member_required
def list_all_verifications(request):
    return render(request, 'list_all_verifications.html', {
        'confirmations' : Confirmation.objects.all()
    })

@staff_member_required
def list_interested_members(request):
    return render(request, 'list_all_interested_members.html', {
        'data' : WordPress.get_interested_members(5)
    })

@staff_member_required
def list_interested_members_csv(request):
    data = WordPress.get_interested_members(5)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="members.csv"'
    csv_data = [['committee', 'name', 'email']]
    for committee, items in data.items():
        for member in items:
            csv_data.append([committee, member[0], member[1]])

    writer = csv.writer(response)
    for row in csv_data:
        writer.writerow(row)
    return response

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
    props, data = WordPress.get_students_data(request.user.username, as_dict=True)
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


    generator = VerifyTokenGenerator()
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
    props, data = WordPress.get_students_data(request.user.username, as_dict=True)
    data = data[0]
    if request.user.confirmations.filter(date__gt=begin, date__lt=end).count() > 0:
        return render(request, 'base.html', {
            'message' : 'You are already verified as student of {}!'.format(data['footloose_institution'])
        })

    generator = VerifyTokenGenerator()

    if not generator.check_token(request.user, token):
        return render(request, 'base.html', {
            'message' : 'Invalid token!'
        })

    c = Confirmation(date=date.today(), user=request.user, email=data['footloose_tuemail_verific'] if data['footloose_institution'] == 'Eindhoven University of Technology' else data['footloose_fontys_verific'])
    c.save()

    return render(request, 'base.html', {
        'message' : 'Email verified! You can now close this tab.'
    })