from django.urls import path
from . import views

app_name = 'analysis'
urlpatterns = [
    path('import/', views.load_members, name='importmembers'),
    path('upload/subscriptions/', views.upload_subscriptions, name='uploadsubscriptions'),
    path('stats/', views.stats, name='stats'),
]