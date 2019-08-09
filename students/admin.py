from django.contrib import admin
from .models import *

admin.site.register(StudentMeta)
admin.site.register(Confirmation)
admin.site.register(VerifyToken)
