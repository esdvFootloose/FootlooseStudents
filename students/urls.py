from django.urls import path
from . import views

app_name = 'students'
urlpatterns = [
    path('list/', views.list_all_students, name='listall'),
    path('list/csv/', views.list_all_students_csv, name='listallcsv')
]