from django.shortcuts import render
from students.wordpress import WordPress
from .models import Member, Cursus
from django.contrib.admin.views.decorators import staff_member_required
from .forms import XlsxUpload
from io import BytesIO
from openpyxl import load_workbook
from django.db.models import Q
import yaml

@staff_member_required
def load_members(request):
    #TODO: also import board and ict committee members (other UM role on site)
    #TODO: confirmation form before deletion

    Member.objects.all().delete()

    props, data = WordPress.get_students_data()

    for mdata in data:
        m = Member()
        m.load_from_csv(props, mdata)
        m.save()

    return render(request, 'base.html', {
        'message' : 'All members imported to analysis database!'
    })

@staff_member_required
def upload_subscriptions(request):
    #TODO: do something on UTF-8
    if request.method == 'POST':
        form = XlsxUpload(request.POST, request.FILES)
        if form.is_valid():
            file_in_memory = request.FILES['file'].read()
            wb = load_workbook(filename=BytesIO(file_in_memory), read_only=True)
            Cursus.objects.all().delete()
            for sheet in wb.worksheets:
                c = Cursus(name=sheet.title)
                c.save()
                iterrows = sheet.iter_rows()
                next(iterrows) #skip first row
                for row in iterrows:
                    data = list(row)
                    if data[0].value is None:
                        continue
                    try:
                        m = Member.objects.get(first_name=data[0].value.lower(), last_name=data[1].value.lower())
                    except Member.DoesNotExist:
                        print("Could not find {} {} for {}".format(data[0].value.lower(), data[1].value.lower(), c))
                        continue
                    m.subscriptions.add(c)
                    m.save()
            return render(request, 'base.html', {
                'message' : 'subscriptions imported'
            })
    else:
        form = XlsxUpload()
    return render(request, 'upload.html', {
        'form' : form
    })

@staff_member_required
def stats(request):

    total_ammount = Member.objects.count()
    total_ammount_student = Member.objects.filter(student=True).count()
    total_ammount_tue = Member.objects.filter(institute=0).count()
    total_ammount_fon = Member.objects.filter(institute=1).count()

    percentage_student = round(total_ammount_student / total_ammount *100, 2)
    percentage_tue = round(total_ammount_tue / total_ammount_student * 100, 2)
    percentage_fon = round(total_ammount_fon / total_ammount_student * 100, 2)

    men_ammount = Member.objects.filter(gender='M').count()
    woman_ammount = Member.objects.filter(gender='F').count()

    percentage_men = round(men_ammount / total_ammount * 100, 2)
    percentage_woman = round(woman_ammount / total_ammount * 100, 2)
    #TODO: add stats per course
    data = {
        'total_ammount' : total_ammount,
        'total_ammount_student' : total_ammount_student,
        'total_ammount_tue' : total_ammount_tue,
        'total_ammount_fon' : total_ammount_fon,
        'percentage_student' : percentage_student,
        'percentage_tue' : percentage_tue,
        'percentage_fon' : percentage_fon,
        'men_ammount' : men_ammount,
        'woman_ammount' : woman_ammount,
        'percentage_men' : percentage_men,
        'percentage_woman' : percentage_woman
    }

    with open('stats.yaml', 'w') as stream:
        yaml.dump(data, stream, default_flow_style=False)

    return render(request, 'stats.html', {
        'data' : data
    })