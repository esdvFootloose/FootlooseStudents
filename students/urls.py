from django.urls import path
from . import views

app_name = 'students'
urlpatterns = [
    path('list/', views.list_all_students, name='listall'),
    path('list/csv/', views.list_all_students_csv, name='listallcsv'),
    path('list/submissions/', views.list_all_submissions, name='listallsubmissions'),
    path('list/submissions/csv/', views.list_all_submissions_csv, name='listallsubmissionscsv'),
    path('verify/request/', views.verify_student_request, name='verify_request'),
    path('verify/confirm/<slug:token>/', views.verify_student_confirm, name='verify_confirm'),
]