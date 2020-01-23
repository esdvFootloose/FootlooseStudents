from django.urls import path
from . import views

app_name = 'students'
urlpatterns = [
    path('stats/', views.stats, name='stats'),
    path('list/submissions/', views.list_submissions, name='listsubmissions'),
    path('list/submissions/csv/', views.list_all_submissions_csv, name='listallsubmissionscsv'),
    # path('list/submissions/csv/unmerged/', views.list_all_submissions_unmerged_csv, name='listallsubmissionsunmergedcsv'),

    path('list/interested/', views.list_interested_members, name='listinterestedmembers'),
    path('list/interested/csv/', views.list_interested_members_csv, name='listinterestedmemberscsv'),

    path('verify/request/', views.verify_student_request, name='verify_request'),
    path('verify/confirm/<slug:token>/', views.verify_student_confirm, name='verify_confirm'),
    path('list/verifications/', views.list_all_verifications, name='listverifications'),

    path('list/invalids/', views.list_invalids, name='listinvalids'),
    path('list/invalids/<slug:t>/', views.list_invalids, name='listinvalids'),

    path('list/<slug:type>/', views.list_all_students, name='listall'),
    path('list/<slug:type>/<int:onlynonverified>/', views.list_all_students, name='listall'),
    path('list/<slug:type>/csv/', views.list_all_students_csv, name='listallcsv'),
]
