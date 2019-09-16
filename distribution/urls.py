from django.urls import path
from . import views

app_name = 'distribution'
urlpatterns = [
    path('api/activemember/', views.api_toggle_active_member, name='api_toggleactivemember'),
]