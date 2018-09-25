from django.db import models
from django.contrib.auth.models import User

class Confirmation(models.Model):
    date = models.DateField()
    email = models.EmailField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='confirmations')

class VerifyToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=20)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verifytoken')