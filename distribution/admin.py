from django.contrib import admin
from .models import *

class DistributionAdmin(admin.ModelAdmin):
    search_fields = ['couple__leader__username', 'couple__follower__username']
    list_filter = ['course','admitted']

admin.site.register(CourseType)
admin.site.register(Course)
admin.site.register(Couple)
admin.site.register(Distribution, DistributionAdmin)
