from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
import csv
from django.http import HttpResponse, HttpResponseBadRequest
from .util import VerifyTokenGenerator, send_student_verification_mail
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import Confirmation, VerifyToken
from .wordpress import WordPress
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from ipware import get_client_ip
from distribution.models import Distribution
import io
import matplotlib.pyplot as plt
from django.utils.safestring import mark_safe

@staff_member_required
def list_all_submissions_csv(request):
    props, data_raw = WordPress.get_subscriptions(3, aslist=True)

    data = []
    for sub in data_raw:
        row = []
        for v in sub:
            if type(v) == bool:
                row.append(1 if v else 0)
            else:
                row.append(v)
        data.append(row)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="submissions.csv"'

    writer = csv.writer(response)
    writer.writerow(props)
    writer.writerows(data)

    return response

@staff_member_required
def list_submissions(request):
    props, data = WordPress.get_subscriptions(3, aslist=True)

    return render(request, 'list_all_submissions.html', {
        'props' : props,
        'submissions' : data,
    })


@staff_member_required
def list_all_students_csv(request, type):
    if type == "wp":
        props, students = WordPress.get_students_data()
    elif type == "db":
        props = ['username', 'email', 'student', 'verificated', 'verification email']
        students = []
        for usr in User.objects.filter(is_staff=False):
            student = "no"
            if hasattr(usr, "studentmeta"):
                if usr.studentmeta.is_student:
                    student = "yes"
            students.append([
                usr.username,
                usr.email,
                student,
                "yes" if hasattr(usr, "verification") else "no",
                usr.verification.email if hasattr(usr, "verification") else "",
            ])
    else:
        props = []
        students = []

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(props)
    for student in students:
        writer.writerow(student)


    return response

@staff_member_required
def list_all_students(request, type, onlynonverified=0):
    if type == "wp":
        props, data = WordPress.get_students_data()
    elif type == "db":
        props = ['Username', 'Email', 'Student', 'Verified', 'Verification Email', 'Active Member']
        data = []
        if onlynonverified:
            QS = User.objects.filter(studentmeta__isnull=False).filter(verification__isnull=True, studentmeta__is_student=True)
        else:
            QS = User.objects.filter(studentmeta__isnull=False)
        for usr in QS:
            data.append([
                usr.username,
                usr.email,
                mark_safe('<input type="checkbox" data-role="switch" data-material="true"'
                          ' onchange="toggle_student({})" {}/>'.format(usr.studentmeta.userid,
                                                              "checked" if usr.studentmeta.is_student else "")),
                "yes" if hasattr(usr, "verification") else "no",
                usr.verification.email if hasattr(usr, "verification") else "",
                mark_safe('<input type="checkbox" data-role="switch" data-material="true"'
                          ' onchange="toggle_activemember({})" {}/>'.format(usr.studentmeta.userid,
                                                              "checked" if usr.studentmeta.is_activemember else ""))
            ])
    else:
        return HttpResponseBadRequest()

    return render(request, 'list_all_students.html', {
        'props' : props,
        'students' : data,
        'type': type
    })

def calculate_age(born):
    today = date.today()
    if today.replace(year=born.year) < today:
        # birthday already passed
        return today.year - born. year
    else:
        return today.year - born.year - 1

def createpie(data):
    fig = plt.figure()

    plt.pie([float(v) for v in data.values()], labels=list(data.keys()), autopct='%1.0f%%')

    buf = io.StringIO()
    fig.savefig(buf, format='svg')
    buf.seek(0)

    return buf.read()

@staff_member_required
def stats(request):
    data_studies = {}
    data_gender = {'male': 0, 'female': 0, 'other': 0}
    data_institute = {'tue': 0, 'fontys': 0, 'other': 0}
    data_student = {'yes': 0, 'no': 0}

    users_counted = []
    
    # warm up cache
    WordPress.get_students_data(as_dict=True)

    dists = Distribution.objects.filter(admitted=True)
    for distr in dists:
        usrs = [distr.couple.leader]
        if distr.couple.follower is not None:
            usrs.append(distr.couple.follower)
        for usr in usrs:
            if usr.pk not in users_counted:
                try:
                    d = WordPress.get_students_data(username=usr.username, as_dict=True)[1][0]
                except IndexError:
                    continue
                
                if d['gender'][0].lower() == 'm':
                    data_gender['male'] += 1
                elif d['gender'][0].lower() == 'f':
                    data_gender['female'] += 1
                else:
                    data_gender['other'] += 1

                if d['footloose_student'] == 'Yes':
                    data_student['yes'] += 1
                    if d['footloose_institution'] == 'Eindhoven University of Technology':
                        data_institute ['tue'] += 1

                        if d['footloose_faculty'] not in data_studies:
                            data_studies[d['footloose_faculty']] = 1
                        else:
                            data_studies[d['footloose_faculty']] += 1

                    elif d['footloose_institution'] =='Fontys':
                        data_institute['fontys'] += 1
                    else:
                        data_institute['other'] += 1

                    
                else:
                    data_student['no'] += 1



    return render(request, 'stats.html', {'studies':data_studies, 'gender': data_gender, 'institute': data_institute, 'student': data_student, 'studies_chart': mark_safe(createpie(data_studies)), 'institute_chart': mark_safe(createpie(data_institute)), 'student_chart': mark_safe(createpie(data_student)), 'gender_chart': mark_safe(createpie(data_gender)) })


@staff_member_required
def list_invalids(request, t='table'):
    users = User.objects.filter(studentmeta__is_student=True)
    invalids = []
    for usr in users:
        props, data = WordPress.get_students_data(usr.username, as_dict=True)
        data = data[0]
        if data['footloose_institution'] == 'Eindhoven University of Technology':
            domain = data['footloose_tuemail_verific'].split('@')[-1].strip()
            if domain not in ['student.tue.nl', 'tue.nl']:
                invalids.append([
                        usr.username,
                        data['footloose_institution'],
                        data['footloose_tuemail_verific'],
                        data['email']
                    ]
                )
        elif data['footloose_institution'] == 'Fontys':
            domain = data['footloose_fontys_verific'].split('@')[-1].strip()
            if domain not in ['student.fontys.nl', 'fontys.nl']:
                invalids.append([
                        usr.username,
                        data['footloose_institution'],
                        data['footloose_fontys_verific'],
                        data['email']
                    ]
                )
        else:
            continue

    if t == 'table':
        return render(request, 'list_all_invalids.html', {
            'props': ['username', 'institution', 'student email', 'contact email'],
            'students': invalids
        })
    elif t == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="invalids.csv"'

        writer = csv.writer(response)
        writer.writerow(['username', 'institution', 'student email', 'contact email'])
        writer.writerows(invalids)

        return response



@staff_member_required
def list_all_verifications(request):
    return render(request, 'list_all_verifications.html', {
        'confirmations': Confirmation.objects.all(),
        'numconfirmations': Confirmation.objects.count(),
        'numverifytokens': VerifyToken.objects.count()
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


@login_required
def verify_student_request(request):
    if request.user.is_staff:
        return render(request, 'base.html', {
            'message' : 'Only for students'
        })

    if hasattr(request.user, "verification"):
        return render(request, 'base.html', {
            'message' : 'You are already verified as student of {}!'.format(request.user.studentmeta.institute)
        })
    if request.method != 'POST':
        props, data = WordPress.get_students_data(request.user.username, as_dict=True)
        data = data[0]
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

    send_student_verification_mail(request.user)

    return render(request, 'base.html', { 'message' : 'Verification link send' })



def verify_student_confirm(request, token):
    try:
        tokenobj = VerifyToken.objects.get(token=token)
    except VerifyToken.DoesNotExist:
        return render(request, 'base.html', {
            'message' : 'This token is invalid or already used. Please contact ict@esdvfootloose.nl with your name and emailaddress'
        })

    if hasattr(request.user, "verification"):
        return render(request, 'base.html', {
            'message' : 'You are already verified as student of {}'.format(request.user.studentmeta.institute)
        })

    if request.method == "POST":
        generator = VerifyTokenGenerator()

        if not generator.check_token(tokenobj.user, token):
            return render(request, 'base.html', {
                'message' : 'Invalid token!'
            })

        c = Confirmation(date=date.today(), user=tokenobj.user, email=tokenobj.email, ip=get_client_ip(request)[0])
        c.save()
        tokenobj.delete()

        return render(request, 'base.html', {
            'message' : 'Email verified! You can now close this tab.'
        })

    else:
        data = WordPress.get_students_data(tokenobj.user.username, as_dict=True)[1][0]
        email = data['footloose_tuemail_verific'] if data['footloose_institution'] == 'Eindhoven University of Technology' else \
            data['footloose_fontys_verific']
        return render(request, 'confirmform.html', {
            'email':  email
        })
