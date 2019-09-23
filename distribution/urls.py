from django.urls import path
from . import views

app_name = 'distribution'
urlpatterns = [
    path('api/activemember/', views.api_toggle_active_member, name='api_toggleactivemember'),
    path('api/student/', views.api_toggle_student, name='api_togglestudent'),
    path('api/create/couple/', views.api_create_couple, name='api_createcouple'),
    path('api/distribution/save/', views.api_save_distributions, name='api_savedistributions'),
    path('api/distribution/save/<int:pk>/', views.api_save_distributions, name='api_savedistributions'),

    path('listtypes/', views.list_course_types, name='listcoursetypes'),
    path('distribute/manual/<int:pk>/', views.manual_distribute, name='manualdistribute'),
    path('distribute/manual/step/1/', views.automatic_distribute_step1, name='automaticdistribute_step1'),
    path('distribute/manual/step/2/', views.automatic_distribute_step2, name='automaticdistribute_step2')
]