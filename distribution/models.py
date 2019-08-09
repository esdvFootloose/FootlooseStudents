from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=512)
    level = models.IntegerField()

    def __str__(self):
        return "{} {}".format(self.name, self.level)