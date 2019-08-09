from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    path('students/', include('students.urls')),
    # path('analysis/', include('analysis.urls')),
]
