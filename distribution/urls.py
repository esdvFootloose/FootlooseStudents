from django.urls import path
from . import views

app_name = 'distribution'
urlpatterns = [
    path('api/activemember/', views.api_toggle_active_member, name='api_toggleactivemember'),
    path('listtypes/', views.list_course_types, name='listcoursetypes'),
    path('distribute/manual/<int:pk>/', views.manual_distribute, name='manualdistribute'),
]