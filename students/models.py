from django.db import models
from django.contrib.auth.models import User

class StudentMeta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentmeta')
    is_student = models.BooleanField()
    userid = models.IntegerField()


class Confirmation(models.Model):
    date = models.DateField()
    email = models.EmailField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification')

class VerifyToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=20)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verifytoken')