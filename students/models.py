from django.db import models
from django.contrib.auth.models import User
import datetime

class StudentMeta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentmeta')
    is_student = models.BooleanField()
    userid = models.IntegerField()
    institute = models.CharField(max_length=512, default="")
    is_activemember = models.BooleanField(default=False)

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)


class Confirmation(models.Model):
    date = models.DateField()
    email = models.EmailField()
    ip = models.GenericIPAddressField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification')

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)


class VerifyToken(models.Model):
    created = models.DateField(default=datetime.date.today)
    reminded = models.DateField(default=datetime.date.today)
    email = models.EmailField()
    token = models.CharField(max_length=32)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verifytoken')

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)